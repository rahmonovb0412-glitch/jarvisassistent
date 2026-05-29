"""
Jarvis Agent - Asosiy FastAPI server
WebSocket orqali real-time muloqot + ElevenLabs TTS
"""

import os
import sys
import json
import asyncio

# sys.path ga loyiha root ni qo'shamiz — import xatolarini oldini olish uchun
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv(os.path.join(ROOT, '.env'))

# ── Lazy import: xato chiqsa ham server ishga tushsin ─────────────────────────
try:
    import aiofiles
    AIOFILES_OK = True
except ImportError:
    AIOFILES_OK = False
    print("⚠️  aiofiles topilmadi — fayl yuklash ishlamaydi. pip install aiofiles")

try:
    from backend.agent import JarvisAgent
    agent = JarvisAgent()
    AGENT_OK = True
except Exception as e:
    AGENT_OK = False
    agent = None
    print(f"⚠️  Agent yuklashda xato: {e}")

try:
    from tts.uzbek_tts import async_text_to_speech, get_available_voices
    TTS_OK = True
except Exception as e:
    TTS_OK = False
    print(f"⚠️  TTS yuklashda xato: {e}")
    async def async_text_to_speech(text): return ""
    def get_available_voices(): return []

# ──────────────────────────────────────────────────────────────────────────────

WORKSPACE = os.getenv("WORKSPACE_DIR", os.path.join(ROOT, "workspace"))
os.makedirs(WORKSPACE, exist_ok=True)

TTS_MAX_LENGTH = 1200

app = FastAPI(title="Jarvis Agent", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = os.path.join(ROOT, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/")
async def root():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("""
    <h1 style='font-family:sans-serif;color:#4f8ef7;padding:40px'>
        🤖 Jarvis Agent ishlamoqda!<br>
        <small style='font-size:16px;color:#888'>
        Agar frontend ko'rinmasa, frontend/index.html mavjudligini tekshiring.
        </small>
    </h1>""")


@app.get("/health")
async def health():
    el_key = os.getenv("ELEVENLABS_API_KEY", "")
    return {
        "status": "ok",
        "version": "2.0",
        "agent": AGENT_OK,
        "tts": "ElevenLabs" if el_key and "your_" not in el_key else "gTTS",
        "aiofiles": AIOFILES_OK,
        "telegram": bool(os.getenv("TELEGRAM_API_ID")),
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
    }


@app.post("/reset")
async def reset_chat():
    if agent:
        agent.reset_conversation()
    return {"success": True, "message": "Suhbat tozalandi"}


@app.get("/voices")
async def voices():
    v = get_available_voices()
    return {"success": True, "voices": v, "count": len(v)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Yangi ulanish")

    if not AGENT_OK:
        await websocket.send_text(json.dumps({
            "type": "error",
            "content": "⚠️ Agent yuklanmadi. Terminalda xatoni tekshiring."
        }))
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_text()
            msg_data = json.loads(data)
            user_msg = msg_data.get("message", "").strip()
            tts_on   = msg_data.get("tts", True)

            if not user_msg:
                continue

            async def send_step(txt):
                await websocket.send_text(json.dumps({"type": "step", "content": txt}))

            try:
                await websocket.send_text(json.dumps({
                    "type": "thinking", "content": "Jarvis fikrlamoqda..."
                }))

                answer = await agent.think_and_act(user_msg, on_step=send_step)

                audio_b64  = ""
                tts_source = ""
                if tts_on and TTS_OK and len(answer) <= TTS_MAX_LENGTH:
                    try:
                        el = os.getenv("ELEVENLABS_API_KEY", "")
                        tts_source = "ElevenLabs" if el and "your_" not in el else "gTTS"
                        await send_step(f"🔊 {tts_source} ovoz yaratilmoqda...")
                        audio_b64 = await async_text_to_speech(answer)
                    except Exception as e:
                        print(f"TTS xato: {e}")

                await websocket.send_text(json.dumps({
                    "type": "answer",
                    "content": answer,
                    "audio": audio_b64,
                    "tts_source": tts_source
                }))

            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error", "content": f"Xato: {str(e)}"
                }))

    except WebSocketDisconnect:
        print("❌ Ulanish uzildi")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        save_path = os.path.join(WORKSPACE, file.filename)
        content = await file.read()
        if AIOFILES_OK:
            import aiofiles
            async with aiofiles.open(save_path, "wb") as f:
                await f.write(content)
        else:
            with open(save_path, "wb") as f:
                f.write(content)
        return {"success": True, "message": f"✅ {file.filename} yuklandi", "size": len(content)}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/files")
async def get_files():
    try:
        files = [
            {"name": e.name, "type": "folder" if e.is_dir() else "file",
             "size": e.stat().st_size if e.is_file() else 0}
            for e in os.scandir(WORKSPACE)
        ]
        return {"success": True, "files": files}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    el   = os.getenv("ELEVENLABS_API_KEY", "")
    tts  = "ElevenLabs 🎙️" if el and "your_" not in el else "gTTS"
    print(f"\n🤖 Jarvis Agent v2.0")
    print(f"🌐 Brauzer   : http://localhost:{port}")
    print(f"🔊 TTS       : {tts}")
    print(f"📁 Workspace : {os.path.abspath(WORKSPACE)}")
    print(f"✅ Agent     : {'Tayyor' if AGENT_OK else 'XATO - terminalga qarang'}\n")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)
