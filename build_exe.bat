@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo.
echo ================================================
echo   JARVIS - .EXE FAYL QURISH (Windows)
echo ================================================
echo.
echo Bu jarayon Jarvis.exe faylini yaratadi.
echo Tayyor bo'lgach, Python kerak bo'lmaydi!
echo.

:: PyInstaller o'rnatish
echo [1/2] PyInstaller o'rnatilmoqda...
python -m pip install pyinstaller --quiet

:: .exe qurish
echo [2/2] Jarvis.exe quirilmoqda (bu biroz vaqt oladi)...
python -m PyInstaller ^
  --noconsole ^
  --onefile ^
  --name "Jarvis" ^
  --add-data "frontend;frontend" ^
  --add-data "backend;backend" ^
  --add-data "tools;tools" ^
  --add-data "tts;tts" ^
  --add-data "stt;stt" ^
  --add-data ".env;." ^
  --hidden-import uvicorn ^
  --hidden-import fastapi ^
  --hidden-import webview ^
  --hidden-import google.generativeai ^
  app.py

echo.
if exist "dist\Jarvis.exe" (
    echo ================================================
    echo  [OK] TAYYOR! Jarvis.exe yaratildi:
    echo       dist\Jarvis.exe
    echo  Endi shu faylni 2 marta bosib ishlatishingiz mumkin!
    echo ================================================
) else (
    echo [XATO] .exe yaratilmadi. Yuqoridagi xatolarni tekshiring.
)
echo.
pause
