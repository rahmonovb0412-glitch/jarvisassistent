"""
Jarvis TTS - Matndan nutqqa aylantirish
ElevenLabs (sifatli, tabiiy) → gTTS (zaxira) ketma-ketligi
"""

import os
import io
import base64
import asyncio
import requests
from gtts import gTTS

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# ElevenLabs ovoz sozlamalari
# Multilingual v2 model O'zbek tilini yaxshi talaffuz qiladi
ELEVENLABS_MODEL   = "eleven_multilingual_v2"

# Ovoz tanlash: "Rachel" (ayol, tabiiy) yoki "Adam" (erkak)
# Barcha ovozlar: https://elevenlabs.io/voice-library
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "s3TPKV1kjDlVtZbl4Ksh")

VOICE_SETTINGS = {
    "stability": 0.5,          # 0-1: past=ekspressiv, yuqori=barqaror
    "similarity_boost": 0.75,  # 0-1: ovoz o'xshashligi
    "style": 0.3,              # 0-1: stil kuchaytirish
    "use_speaker_boost": True  # Ovoz aniqligini oshirish
}


def _elevenlabs_tts(text: str) -> bytes | None:
    """ElevenLabs API orqali audio yaratadi, bytes qaytaradi"""
    if not ELEVENLABS_API_KEY:
        return None

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }

    payload = {
        "text": text,
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": VOICE_SETTINGS
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            return resp.content
        else:
            print(f"ElevenLabs xato {resp.status_code}: {resp.text[:200]}")
            return None
    except requests.exceptions.Timeout:
        print("ElevenLabs timeout - gTTS ga o'tilmoqda")
        return None
    except Exception as e:
        print(f"ElevenLabs ulanish xatosi: {e}")
        return None


def _gtts_tts(text: str) -> bytes | None:
    """gTTS (Google TTS) zaxira sifatida ishlatiladi"""
    try:
        tts = gTTS(text=text, lang="uz", slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf.read()
    except Exception:
        try:
            # O'zbek ishlamasa rus tilida urinib ko'r
            tts = gTTS(text=text, lang="ru", slow=False)
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return buf.read()
        except Exception as e:
            print(f"gTTS xato: {e}")
            return None


def text_to_speech_base64(text: str) -> str:
    """
    Matnni audio ga aylantiradi, base64 string qaytaradi.
    1-usul: ElevenLabs (sifatli, tabiiy ovoz)
    2-usul: gTTS (zaxira)
    """
    if not text or not text.strip():
        return ""

    # Juda uzun matnni qisqartirish (ElevenLabs limit)
    clean = text.strip()
    if len(clean) > 2500:
        clean = clean[:2500] + "..."

    # 1. ElevenLabs
    audio_bytes = _elevenlabs_tts(clean)
    source = "ElevenLabs"

    # 2. Zaxira: gTTS
    if not audio_bytes:
        audio_bytes = _gtts_tts(clean)
        source = "gTTS"

    if not audio_bytes:
        return ""

    print(f"🔊 TTS ({source}): {len(clean)} belgi → {len(audio_bytes)} bayt audio")
    return base64.b64encode(audio_bytes).decode("utf-8")


async def async_text_to_speech(text: str) -> str:
    """Async versiyasi - main.py da ishlatiladi"""
    return await asyncio.to_thread(text_to_speech_base64, text)


def save_audio_file(text: str, filepath: str) -> bool:
    """Audio ni faylga saqlaydi"""
    try:
        audio_bytes = _elevenlabs_tts(text) or _gtts_tts(text)
        if not audio_bytes:
            return False
        with open(filepath, "wb") as f:
            f.write(audio_bytes)
        return True
    except Exception as e:
        print(f"Audio saqlash xato: {e}")
        return False


def get_available_voices() -> list:
    """ElevenLabs dagi mavjud ovozlar ro'yxatini oladi"""
    if not ELEVENLABS_API_KEY:
        return []
    try:
        resp = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers={"xi-api-key": ELEVENLABS_API_KEY},
            timeout=10
        )
        if resp.status_code == 200:
            voices = resp.json().get("voices", [])
            return [{"id": v["voice_id"], "name": v["name"]} for v in voices]
        return []
    except Exception:
        return []
