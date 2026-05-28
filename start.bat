@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo.
echo ╔════════════════════════════════════╗
echo ║      JARVIS AGENT - O'ZBEK AI      ║
echo ╚════════════════════════════════════╝
echo.

:: .env faylini tekshirish
if not exist ".env" (
    echo ⚠️  .env fayli topilmadi!
    echo    .env.example dan .env yarating
    echo    va GEMINI_API_KEY ni kiriting
    pause
    exit /b 1
)

:: Paketlarni o'rnatish
echo 📦 Kerakli paketlar o'rnatilmoqda...
pip install -r requirements.txt -q

:: Workspace yaratish
if not exist "workspace" mkdir workspace

echo.
echo 🚀 Jarvis ishga tushmoqda...
echo 🌐 Brauzer: http://localhost:8000
echo    (Ctrl+C bilan to'xtatish)
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
