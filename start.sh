#!/bin/bash
# Jarvis Agent - Ishga tushirish skripti (Linux/Mac)

cd "$(dirname "$0")"

echo ""
echo "╔════════════════════════════════════╗"
echo "║      JARVIS AGENT - O'ZBEK AI      ║"
echo "╚════════════════════════════════════╝"
echo ""

# .env faylini tekshirish
if [ ! -f ".env" ]; then
    echo "⚠️  .env fayli topilmadi!"
    echo "   .env.example faylini .env ga nusxa oling"
    echo "   va GEMINI_API_KEY ni to'ldiring"
    exit 1
fi

# Python tekshirish
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 o'rnatilmagan!"
    exit 1
fi

# Paketlarni o'rnatish
echo "📦 Kerakli paketlar o'rnatilmoqda..."
pip install -r requirements.txt -q

# Workspace yaratish
mkdir -p workspace

echo ""
echo "🚀 Jarvis ishga tushmoqda..."
echo "🌐 Brauzer: http://localhost:8000"
echo "   (Ctrl+C bilan to'xtatish)"
echo ""

python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
