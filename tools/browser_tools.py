"""
Jarvis Browser Tools - Playwright asosida real browser automation
Brauzer ochish, saytlarda harakat qilish, screenshot olish
"""

import os
import asyncio
import subprocess
import urllib.parse
import platform


# ─── ODDIY OCHISH (Playwright kerak emas) ────────────────────────────────────

def _open_url_simple(url: str) -> dict:
    """OS brauzerida URL ochadi"""
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(url)
        elif system == "Darwin":
            subprocess.Popen(["open", url])
        else:
            subprocess.Popen(["xdg-open", url])
        return {"success": True, "url": url}
    except Exception as e:
        return {"success": False, "error": str(e)}


def open_website(site: str) -> dict:
    """Brauzerda istalgan saytni ochadi"""
    common = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "instagram": "https://www.instagram.com",
        "telegram": "https://web.telegram.org",
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.twitter.com",
        "x": "https://www.x.com",
        "tiktok": "https://www.tiktok.com",
        "wikipedia": "https://uz.wikipedia.org",
        "github": "https://www.github.com",
        "gmail": "https://mail.google.com",
    }
    if not site.startswith(("http://", "https://")):
        url = common.get(site.lower()) or (
            f"https://{site}" if "." in site else f"https://www.{site}.com"
        )
    else:
        url = site
    r = _open_url_simple(url)
    return {"success": r["success"], "message": f"✅ Brauzerda ochildi: {url}", "url": url}


def open_instagram(username: str = None, search: str = None) -> dict:
    if username:
        url = f"https://www.instagram.com/{username.lstrip('@')}/"
        msg = f"✅ @{username} profili ochildi"
    elif search:
        url = f"https://www.instagram.com/explore/tags/{urllib.parse.quote_plus(search)}/"
        msg = f"✅ Instagram #{search} ochildi"
    else:
        url = "https://www.instagram.com/"
        msg = "✅ Instagram ochildi"
    r = _open_url_simple(url)
    return {"success": r["success"], "message": msg, "url": url}


def open_telegram_web() -> dict:
    r = _open_url_simple("https://web.telegram.org/")
    return {"success": r["success"], "message": "✅ Telegram Web ochildi"}


def search_youtube(query: str) -> dict:
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"
    r = _open_url_simple(url)
    return {"success": r["success"], "message": f"✅ YouTube: '{query}'", "url": url}


def search_youtube_video(query: str, category: str = None) -> dict:
    q = query
    if category == "music":      q += " official audio"
    elif category == "motivation": q += " motivatsiya"
    elif category == "film":     q += " to'liq kino"
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(q)}"
    r = _open_url_simple(url)
    return {"success": r["success"], "message": f"✅ YouTube: '{q}' ochildi", "url": url}


def play_youtube_music(song: str) -> dict:
    url = f"https://music.youtube.com/search?q={urllib.parse.quote_plus(song)}"
    r = _open_url_simple(url)
    return {"success": r["success"], "message": f"✅ YouTube Music: '{song}' ochildi", "url": url}


def search_google(query: str) -> dict:
    url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"
    r = _open_url_simple(url)
    return {"success": r["success"], "message": f"✅ Google: '{query}' qidiruvchi ochildi", "url": url}


# ─── PLAYWRIGHT BROWSER AUTOMATION ───────────────────────────────────────────

def _playwright_available() -> bool:
    try:
        import playwright
        return True
    except ImportError:
        return False


async def browser_goto(url: str, wait_seconds: int = 3) -> dict:
    """
    Playwright bilan berilgan URL ga kiradi va sahifa mazmunini qaytaradi.
    Headless=False — brauzer ko'rinadi.
    """
    if not _playwright_available():
        return {"success": False, "error": "Playwright o'rnatilmagan. 'pip install playwright && playwright install chromium' buyrug'ini bajaring."}
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=500)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await asyncio.sleep(wait_seconds)
            title = await page.title()
            content = await page.inner_text("body")
            await browser.close()
        return {
            "success": True,
            "url": url,
            "title": title,
            "content": content[:3000]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def browser_click_and_type(url: str, selector: str, text: str) -> dict:
    """
    Sahifadagi elementga bosib matn yozadi.
    selector: CSS selector (masalan: 'input[name=q]')
    """
    if not _playwright_available():
        return {"success": False, "error": "Playwright o'rnatilmagan."}
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=300)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.click(selector)
            await page.type(selector, text, delay=80)
            await asyncio.sleep(1)
            await browser.close()
        return {"success": True, "message": f"✅ '{text}' yozildi: {selector}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def browser_screenshot(url: str) -> dict:
    """Sahifaning screenshot ini oladi va saqlaydi"""
    if not _playwright_available():
        return {"success": False, "error": "Playwright o'rnatilmagan."}
    try:
        from playwright.async_api import async_playwright
        import time
        save_path = os.path.join(
            os.getenv("WORKSPACE_DIR", "./workspace"),
            f"screenshot_{int(time.time())}.png"
        )
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1280, "height": 800})
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.screenshot(path=save_path, full_page=False)
            await browser.close()
        return {
            "success": True,
            "message": f"✅ Screenshot saqlandi: {save_path}",
            "path": save_path
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def browser_search_and_get(query: str, engine: str = "google") -> dict:
    """
    Qidiruv tizimida qidiradi va natijalarni qaytaradi.
    engine: google | bing | youtube
    """
    if not _playwright_available():
        # Fallback: oddiy ochish
        return search_google(query)
    try:
        from playwright.async_api import async_playwright
        if engine == "youtube":
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"
        elif engine == "bing":
            url = f"https://www.bing.com/search?q={urllib.parse.quote_plus(query)}"
        else:
            url = f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}"

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_extra_http_headers({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"})
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2)

            results = []
            if engine == "google":
                items = await page.query_selector_all("div.g")
                for item in items[:8]:
                    try:
                        title_el = await item.query_selector("h3")
                        link_el  = await item.query_selector("a")
                        desc_el  = await item.query_selector("div.VwiC3b, span.aCOpRe")
                        title = await title_el.inner_text() if title_el else ""
                        href  = await link_el.get_attribute("href") if link_el else ""
                        desc  = await desc_el.inner_text() if desc_el else ""
                        if title:
                            results.append({"title": title, "url": href, "desc": desc[:150]})
                    except Exception:
                        continue
            elif engine == "youtube":
                items = await page.query_selector_all("ytd-video-renderer")
                for item in items[:6]:
                    try:
                        title_el = await item.query_selector("#video-title")
                        title = await title_el.inner_text() if title_el else ""
                        href  = await title_el.get_attribute("href") if title_el else ""
                        if title:
                            results.append({"title": title, "url": f"https://youtube.com{href}"})
                    except Exception:
                        continue

            await browser.close()

        _open_url_simple(url)
        return {
            "success": True,
            "query": query,
            "engine": engine,
            "found": len(results),
            "results": results,
            "message": f"✅ '{query}' qidirildi — {len(results)} natija topildi, brauzer ochildi"
        }
    except Exception as e:
        _open_url_simple(url)
        err_short = str(e)[:100]
        return {"success": True, "message": f"✅ Brauzer ochildi (avtomatik qidiruv xato: {err_short})"}


async def browser_youtube_play(query: str) -> dict:
    """
    YouTube da video topib birinchisini ochadi va o'ynaydi
    """
    if not _playwright_available():
        return search_youtube_video(query)
    try:
        from playwright.async_api import async_playwright
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}"
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=400)
            page = await browser.new_page()
            await page.goto(search_url, wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2)
            # Birinchi videoga bosish
            first = await page.query_selector("ytd-video-renderer #video-title")
            video_url = ""
            if first:
                href = await first.get_attribute("href")
                video_url = f"https://www.youtube.com{href}"
                await first.click()
                await asyncio.sleep(3)
            # Brauzer ochiq qoladi — foydalanuvchi ko'radi
            await asyncio.sleep(60)  # 1 daqiqa ochiq
            await browser.close()
        return {
            "success": True,
            "message": f"✅ YouTube da '{query}' videosi ochildi va o'ynayapti!",
            "video_url": video_url
        }
    except Exception as e:
        return search_youtube_video(query)
