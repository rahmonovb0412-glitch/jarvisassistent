#!/bin/bash
# Jarvis Agent - Linux/Mac ishga tushirish skripti

cd "$(dirname "$0")"

echo ""
echo "================================================"
echo "       JARVIS AGENT - O'ZBEK AI v2.0"
echo "================================================"
echo ""

# Python tekshirish
if ! command -v python3 &>/dev/null; then
    echo "[XATO] Python3 topilmadi!"
    echo "sudo apt install python3 python3-pip  (Ubuntu/Debian)"
    echo "brew install python3                  (macOS)"
    exit 1
fi

echo "[1/4] pip yangilanmoqda..."
python3 -m pip install --upgrade pip -q

echo "[2/4] Asosiy paketlar..."
pip3 install fastapi==0.111.0 -q
pip3 install "uvicorn[standard]==0.30.1" -q
pip3 install python-multipart==0.0.9 -q
pip3 install websockets==12.0 -q
pip3 install aiofiles==23.2.1 -q
pip3 install httpx==0.27.0 -q
pip3 install requests==2.32.3 -q

echo "[3/4] AI va qo'shimcha paketlar..."
pip3 install --upgrade google-generativeai -q
pip3 install gTTS==2.5.1 -q
pip3 install pydub==0.25.1 -q
pip3 install psutil==5.9.8 -q
pip3 install python-dotenv==1.0.1 -q
pip3 install pydantic==2.7.4 -q
pip3 install Pillow==10.3.0 -q
pip3 install Telethon==1.36.0 -q
pip3 install SpeechRecognition==3.10.4 -q
pip3 install playwright==1.44.0 -q
pip3 install pywebview==5.1 -q

echo "[3.5/4] Playwright brauzer o'rnatilmoqda (bir marta)..."
python3 -m playwright install chromium 2>/dev/null && echo "    [OK] Playwright tayyor!" || echo "    [SKIP] Playwright o'rnatilmadi (ixtiyoriy)"

echo "[4/4] Tekshirilmoqda..."
python3 -c "import fastapi, uvicorn, aiofiles, google.generativeai, gtts, psutil, dotenv; print('[OK] Barcha paketlar tayyor!')" 2>/dev/null || echo "[OGOHLANTIRISH] Ayrim paketlar yuklanmagan"

# Node.js tekshirish (Remotion uchun)
echo ""
echo "[Node.js] Tekshirilmoqda..."
if command -v node &>/dev/null; then
    NODE_VER=$(node --version)
    echo "[OK] Node.js $NODE_VER topildi"
    echo "[Node] Remotion o'rnatilmoqda..."
    npm install -g @remotion/cli --silent 2>/dev/null && echo "[OK] Remotion tayyor!" || echo "[SKIP] Remotion o'rnatilmadi"
else
    echo "[OGOHLANTIRISH] Node.js topilmadi!"
    echo "  Remotion video render uchun kerak: https://nodejs.org"
    echo "  Jarvis Node.js siz ham ishlaydi, faqat video render bo'lmaydi."
fi

mkdir -p workspace memory

echo ""
echo "================================================"
echo " Jarvis desktop dasturi ochilmoqda..."
echo " (Alohida oyna ochiladi)"
echo "================================================"
echo ""

python3 app.py
