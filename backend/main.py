"""
Jarvis Agent - Asosiy FastAPI server
WebSocket orqali real-time muloqot + ElevenLabs TTS
"""

import os
import sys
import json
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import aiofiles

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

from backend.agent import JarvisAgent
from tts.uzbek_tts import async_text_to_speech, get_available_voices

WORKSPACE = os.getenv("WORKSPACE_DIR", "./workspace")
os.makedirs(WORKSPACE, exist_ok=True)

app = FastAPI(title="Jarvis Agent", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

agent = JarvisAgent()

# TTS foydalanish: qisqa javoblar uchun (≤1200 belgi) ovoz yaratiladi
TTS_MAX_LENGTH = 1200


@app.get("/")
async def root():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>Jarvis Agent ishlamoqda!</h1>")


@app.get("/health")
async def health():
    el_key = os.getenv("ELEVENLABS_API_KEY", "")
    tg_id  = os.getenv("TELEGRAM_API_ID", "")
    return {
        "status": "ok",
        "version": "2.0",
        "tts": "ElevenLabs" if el_key and el_key != "your_elevenlabs_api_key_here" else "gTTS",
        "telegram": "sozlangan" if tg_id else "sozlanmagan",
        "gemini": "sozlangan" if os.getenv("GEMINI_API_KEY") else "sozlanmagan"
    }


@app.post("/reset")
async def reset_chat():
    agent.reset_conversation()
    return {"success": True, "message": "Suhbat tozalandi"}


@app.get("/voices")
async def voices():
    """ElevenLabs da mavjud ovozlar"""
    v = get_available_voices()
    return {"success": True, "voices": v, "count": len(v)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Yangi ulanish")

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "").strip()
            tts_enabled  = message_data.get("tts", True)  # Frontend dan TTS on/off

            if not user_message:
                continue

            async def send_step(step_text: str):
                await websocket.send_text(json.dumps({
                    "type": "step", "content": step_text
                }))

            try:
                await websocket.send_text(json.dumps({
                    "type": "thinking", "content": "Jarvis fikrlamoqda..."
                }))

                answer = await agent.think_and_act(user_message, on_step=send_step)

                # TTS: yoqilgan va javob qisqa bo'lsa
                audio_base64 = ""
                tts_source   = ""
                if tts_enabled and len(answer) <= TTS_MAX_LENGTH:
                    try:
                        el_key = os.getenv("ELEVENLABS_API_KEY", "")
                        tts_source = (
                            "ElevenLabs" if el_key and el_key != "your_elevenlabs_api_key_here"
                            else "gTTS"
                        )
                        await send_step(f"🔊 {tts_source} ovoz yaratilmoqda...")
                        audio_base64 = await async_text_to_speech(answer)
                    except Exception as e:
                        print(f"TTS xato: {e}")

                await websocket.send_text(json.dumps({
                    "type": "answer",
                    "content": answer,
                    "audio": audio_base64,
                    "tts_source": tts_source
                }))

            except Exception as e:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "content": f"Xato: {str(e)}"
                }))

    except WebSocketDisconnect:
        print("❌ Ulanish uzildi")


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        save_path = os.path.join(WORKSPACE, file.filename)
        async with aiofiles.open(save_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        return {
            "success": True,
            "message": f"✅ {file.filename} yuklandi",
            "path": save_path,
            "size": len(content)
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/files")
async def get_files():
    try:
        files = []
        for entry in os.scandir(WORKSPACE):
            files.append({
                "name": entry.name,
                "type": "folder" if entry.is_dir() else "file",
                "size": entry.stat().st_size if entry.is_file() else 0
            })
        return {"success": True, "files": files}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    el   = os.getenv("ELEVENLABS_API_KEY", "")
    tts  = "ElevenLabs 🎙️" if el and el != "your_elevenlabs_api_key_here" else "gTTS (bepul zaxira)"
    print(f"\n🤖 Jarvis Agent v2.0 ishga tushmoqda...")
    print(f"🌐 Brauzer   : http://localhost:{port}")
    print(f"🔊 TTS       : {tts}")
    print(f"📁 Workspace : {os.path.abspath(WORKSPACE)}\n")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
