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
- Python 3.10+
- Google Gemini API kaliti

### Qadamlar

**1. API kalitini sozlash:**
`.env` faylida allaqachon kalitingiz kiritilgan.

**2. Windows da ishga tushirish:**
```
start.bat
```

**3. Linux/Mac da:**
```bash
chmod +x start.sh
./start.sh
```

**4. Brauzerda ochish:**
```
http://localhost:8000
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
jarvis-agent/
├── backend/
│   ├── main.py          # FastAPI server
│   └── agent.py         # Gemini AI agent miyasi
├── frontend/
│   └── index.html       # Web interfeys
├── tools/
│   ├── file_tools.py    # Fayl operatsiyalari
│   ├── system_tools.py  # Sistema operatsiyalari
│   ├── code_tools.py    # Kod operatsiyalari
│   └── web_tools.py     # Internet operatsiyalari
├── tts/
│   └── uzbek_tts.py     # O'zbek ovoz (gTTS)
├── workspace/           # Agent ishlash papkasi
├── .env                 # API kalitlar (yashirin)
├── requirements.txt     # Python paketlar
├── start.sh             # Linux/Mac ishga tushirish
└── start.bat            # Windows ishga tushirish
```
