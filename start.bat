@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo.
echo ================================================
echo        JARVIS AGENT - O'ZBEK AI v2.0
echo ================================================
echo.

:: ── 1. Python tekshirish ─────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [XATO] Python topilmadi!
    echo        https://python.org/downloads dan yuklab ornatib qaytadan ishga tushiring
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo [OK] %%v

:: ── 2. pip yangilash ─────────────────────────────
echo.
echo [1/4] pip yangilanmoqda...
python -m pip install --upgrade pip --quiet 2>nul

:: ── 3. Paketlar (alohida-alohida) ────────────────
echo [2/4] Asosiy paketlar...
python -m pip install fastapi          --quiet
python -m pip install uvicorn          --quiet
python -m pip install python-multipart --quiet
python -m pip install websockets       --quiet
python -m pip install aiofiles         --quiet
python -m pip install httpx            --quiet
python -m pip install requests         --quiet

echo [3/4] AI va qoshimcha paketlar...
python -m pip install --upgrade google-generativeai --quiet
python -m pip install gTTS                --quiet
python -m pip install pydub               --quiet
python -m pip install psutil              --quiet
python -m pip install python-dotenv       --quiet
python -m pip install pydantic            --quiet
python -m pip install Pillow              --quiet
python -m pip install Telethon            --quiet
python -m pip install SpeechRecognition   --quiet
python -m pip install pywebview           --quiet
python -m pip install python-pptx          --quiet

:: ── 4. Tekshirish ─────────────────────────────────
echo [4/4] Tekshirilmoqda...
python -c "import fastapi, uvicorn, aiofiles, psutil, dotenv; print('[OK] Asosiy paketlar tayyor!')"

:: ── 5. Node.js (Remotion uchun, ixtiyoriy) ────────
echo.
node --version >nul 2>&1
if errorlevel 1 (
    echo [INFO] Node.js topilmadi - video render ishlamaydi
    echo        https://nodejs.org dan LTS yuklab ornatish mumkin
) else (
    for /f "tokens=*" %%v in ('node --version') do echo [OK] Node.js %%v
)

:: ── 6. Papkalar ───────────────────────────────────
if not exist "workspace" mkdir workspace
if not exist "memory"    mkdir memory

:: ── 7. .env tekshirish (yo'q bo'lsa avto-yaratish) ─
if not exist ".env" (
    echo [INFO] .env topilmadi - shablondan yaratilmoqda...
    copy ".env.example" ".env" >nul
    echo.
    echo ================================================
    echo  [DIQQAT] .env fayli yaratildi!
    echo  Notepad bilan .env ni oching va GEMINI_API_KEY ni
    echo  to'ldiring: https://aistudio.google.com/app/apikey
    echo ================================================
    echo.
    notepad .env
    pause
)

:: ── 8. Desktop dastur ishga tushirish ─────────────
echo.
echo ================================================
echo  Jarvis desktop dasturi ochilmoqda...
echo  (Alohida oyna ochiladi, terminal yopilmasin)
echo ================================================
echo.

python app.py

echo.
pause
