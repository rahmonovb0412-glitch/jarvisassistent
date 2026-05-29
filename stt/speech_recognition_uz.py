"""
Jarvis STT - Speech to Text (Ovozni matnga aylantirish)
Google Speech Recognition + fallback
"""

import os
import asyncio
import io
import base64
import tempfile


def transcribe_audio_file(audio_path: str, language: str = "uz-UZ") -> dict:
    """Audio faylni matnga aylantiradi"""
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.record(source)

        # 1. Google STT (bepul, internet kerak)
        try:
            text = recognizer.recognize_google(audio, language=language)
            return {"success": True, "text": text, "engine": "Google", "language": language}
        except sr.UnknownValueError:
            return {"success": False, "error": "Ovoz aniqlanmadi"}
        except sr.RequestError as e:
            return {"success": False, "error": f"Google STT xato: {e}"}
    except ImportError:
        return {"success": False, "error": "SpeechRecognition o'rnatilmagan: pip install SpeechRecognition"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def transcribe_audio_base64(audio_base64: str, language: str = "uz-UZ") -> dict:
    """Base64 audio ni matnga aylantiradi (frontend dan kelgan audio uchun)"""
    try:
        audio_bytes = base64.b64decode(audio_base64)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        try:
            result = transcribe_audio_file(tmp_path, language)
            return result
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        return {"success": False, "error": str(e)}


async def async_transcribe(audio_base64: str, language: str = "uz-UZ") -> dict:
    """Async versiya"""
    return await asyncio.to_thread(transcribe_audio_base64, audio_base64, language)


def record_from_mic(duration: int = 5, language: str = "uz-UZ") -> dict:
    """Mikrofondan ovoz yozib matnga aylantiradi"""
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
        try:
            text = recognizer.recognize_google(audio, language=language)
            return {"success": True, "text": text, "engine": "Google"}
        except sr.UnknownValueError:
            return {"success": False, "error": "Ovoz aniqlanmadi"}
        except sr.RequestError as e:
            return {"success": False, "error": f"STT xato: {e}"}
    except ImportError:
        return {"success": False, "error": "SpeechRecognition o'rnatilmagan"}
    except Exception as e:
        return {"success": False, "error": str(e)}
