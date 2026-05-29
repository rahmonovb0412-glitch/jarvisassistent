"""
Jarvis Desktop App - Alohida dastur oynasi (terminal emas!)
PyWebView orqali native desktop oyna ochadi.
FastAPI server orqa fonda ishlaydi.
"""

import os
import sys
import time
import socket
import threading

# Loyiha root ni sys.path ga qo'shish
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

PORT = int(os.getenv("PORT", 8000))
HOST = "127.0.0.1"
URL = f"http://{HOST}:{PORT}"



def _port_open(host: str, port: int) -> bool:
    """Server tayyor bo'lganini tekshiradi"""
    try:
        with socket.create_connection((host, port), timeout=0.5):
            return True
    except OSError:
        return False


def start_server():
    """FastAPI serverni orqa fonda ishga tushiradi"""
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="warning",
    )


def wait_for_server(timeout: int = 30) -> bool:
    """Server tayyor bo'lguncha kutadi"""
    start = time.time()
    while time.time() - start < timeout:
        if _port_open(HOST, PORT):
            return True
        time.sleep(0.3)
    return False



def main():
    print("=" * 50)
    print("  JARVIS - O'zbek AI Agent (Desktop)")
    print("=" * 50)

    # 1. Serverni alohida thread da ishga tushirish
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    print("[1/2] Server ishga tushmoqda...")

    # 2. Server tayyor bo'lguncha kutish
    if not wait_for_server(30):
        print("[XATO] Server 30 soniyada ishga tushmadi!")
        print("       Terminalga 'python -m uvicorn backend.main:app' yozib xatoni ko'ring.")
        input("Chiqish uchun Enter bosing...")
        return
    print("[2/2] Server tayyor! Oyna ochilmoqda...")

    # 3. PyWebView oynasini ochish
    try:
        import webview
    except ImportError:
        print("[XATO] pywebview o'rnatilmagan!")
        print("       pip install pywebview")
        print(f"       Hozircha brauzerda oching: {URL}")
        import webbrowser
        webbrowser.open(URL)
        input("Chiqish uchun Enter bosing...")
        return

    # Native desktop oyna
    window = webview.create_window(
        title="Jarvis — O'zbek AI Agent",
        url=URL,
        width=1100,
        height=760,
        min_size=(820, 600),
        background_color="#050510",
        text_select=True,
        confirm_close=False,
    )

    # Oynani ishga tushirish (GUI thread)
    webview.start(debug=False)


if __name__ == "__main__":
    main()
