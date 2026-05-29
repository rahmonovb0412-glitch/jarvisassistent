# 🤖 Jarvis — O'zbek AI Agent

O'zbek tilida gaplashadigan, barcha vazifalarni bajara oladigan AI agent.

## ✨ Qobiliyatlari

| Soha | Imkoniyatlar |
|------|-------------|
| 📁 Fayllar | Yaratish, o'qish, o'chirish, nusxa, ko'chirish, qidirish |
| 💻 Kod | Yozish, tahlil qilish, tuzatish, ishga tushirish |
| ⚙️ Sistema | Terminal buyruqlar, jarayonlar, paket o'rnatish |
| 🌐 Internet | Qidirish, URL dan ma'lumot olish |
| 🔊 Ovoz | O'zbek tilida gapiradi (TTS) |
| 🎤 Mikrofon | Ovozli buyruqlar (STT) |

## 🚀 O'rnatish va ishga tushirish

### Talablar
- Python 3.10+ (https://python.org dan)
- Google Gemini API kaliti (`.env` da allaqachon bor)

### 🖥️ Desktop dastur (tavsiya etiladi)

Jarvis endi **alohida dastur oynasida** ishlaydi — qora terminal emas, o'z dizayniga ega chiroyli oyna!

**Windows:**
1. `start.bat` ni 2 marta bosing (birinchi marta paketlarni o'rnatadi)
2. Keyingi safar — `Jarvis.vbs` ni bosing (terminalsiz, faqat oyna ochiladi)

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

### 📦 .exe fayl yaratish (Python kerak bo'lmaydi)

`build_exe.bat` ni ishga tushiring → `dist/Jarvis.exe` yaratiladi.
Bu faylni istalgan Windows kompyuterda Python o'rnatmasdan ishlatish mumkin!

### 🌐 Brauzer rejimi (ixtiyoriy)
```bash
python -m uvicorn backend.main:app --port 8000
# keyin brauzerda: http://localhost:8000
```

## 💬 Foydalanish misollari

- *"desktop papkasida salom.txt fayl yarat"*
- *"kompyuter haqida ma'lumot ber"*
- *"Python da kalkulyator kodi yoz"*
- *"requests paketini o'rnat"*
- *"workspace papkasidagi fayllarni ko'rsat"*
- *"sun'iy intellekt haqida internetdan qidir"*

## 📁 Loyiha tuzilishi

```
jarvisassistent/
├── app.py               # 🖥️ Desktop dastur (PyWebView oyna)
├── Jarvis.vbs           # Terminalsiz ishga tushirish (Windows)
├── build_exe.bat        # .exe fayl yaratish
├── backend/
│   ├── main.py          # FastAPI server
│   └── agent.py         # Gemini AI agent miyasi
├── frontend/
│   └── index.html       # Web interfeys (dizayn)
├── tools/
│   ├── file_tools.py    # Fayl operatsiyalari
│   ├── system_tools.py  # Sistema operatsiyalari
│   ├── code_tools.py    # Kod operatsiyalari
│   ├── web_tools.py     # Internet operatsiyalari
│   ├── browser_tools.py # Brauzer automation (Playwright)
│   ├── weather_tools.py # Ob-havo
│   ├── telegram_tools.py# Telegram
│   └── remotion_tools.py# Video render
├── tts/uzbek_tts.py     # O'zbek ovoz (ElevenLabs + gTTS)
├── stt/                 # Ovozni matnga (STT)
├── workspace/           # Agent ishlash papkasi
├── .env                 # API kalitlar (yashirin)
├── requirements.txt     # Python paketlar
├── start.sh             # Linux/Mac ishga tushirish
└── start.bat            # Windows ishga tushirish
```
