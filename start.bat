@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo.
echo ================================================
echo        JARVIS AGENT - O'ZBEK AI v2.0
echo ================================================
echo.

:: Python borligini tekshirish
python --version >nul 2>&1
if errorlevel 1 (
    echo [XATO] Python topilmadi!
    echo Python ni https://python.org dan yuklab o'rnating
    pause
    exit /b 1
)

:: pip ni yangilash
echo [1/4] pip yangilanmoqda...
python -m pip install --upgrade pip -q

:: Har birini alohida o'rnatish (xato chiqsa ham davom etadi)
echo [2/4] Asosiy paketlar o'rnatilmoqda...
pip install fastapi==0.111.0 -q
pip install "uvicorn[standard]==0.30.1" -q
pip install python-multipart==0.0.9 -q
pip install websockets==12.0 -q
pip install aiofiles==23.2.1 -q
pip install httpx==0.27.0 -q
pip install requests==2.32.3 -q

echo [3/4] AI va qo'shimcha paketlar...
pip install google-generativeai==0.7.2 -q
pip install gTTS==2.5.1 -q
pip install pydub==0.25.1 -q
pip install psutil==5.9.8 -q
pip install python-dotenv==1.0.1 -q
pip install pydantic==2.7.4 -q
pip install Pillow==10.3.0 -q
pip install Telethon==1.36.0 -q
pip install SpeechRecognition==3.10.4 -q
pip install playwright==1.44.0 -q

echo [3.5/4] Playwright brauzer o'rnatilmoqda (bir marta)...
playwright install chromium 2>nul
if errorlevel 1 (
    python -m playwright install chromium 2>nul
)
echo     [OK] Playwright tayyor!

echo [4/4] Tekshirilmoqda...
python -c "import fastapi, uvicorn, aiofiles, google.generativeai, gtts, psutil, dotenv; print('[OK] Barcha paketlar tayyor!')"
if errorlevel 1 (
    echo [OGOHLANTIRISH] Ayrim paketlar yuklanmagan bo'lishi mumkin
)

:: workspace papkasi yaratish
if not exist "workspace" mkdir workspace
if not exist "memory" mkdir memory

echo.
echo ================================================
echo  Jarvis ishga tushmoqda...
echo  Brauzer: http://localhost:8000
echo  Toxtatish uchun: Ctrl+C
echo ================================================
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

echo.
echo Jarvis toxtatildi.
pause
