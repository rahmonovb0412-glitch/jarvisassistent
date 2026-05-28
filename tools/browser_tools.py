"""
Brauzer va web ochish toollari
YouTube, Instagram, va boshqa saytlarni ochish
"""

import subprocess
import platform
import urllib.parse
import os
import sys


def open_url(url: str) -> dict:
    """Brauzerda URL ochadi"""
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(url)
        elif system == "Darwin":  # macOS
            subprocess.Popen(["open", url])
        else:  # Linux
            subprocess.Popen(["xdg-open", url])
        return {"success": True, "message": f"✅ Brauzerda ochildi: {url}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_youtube(query: str, autoplay: bool = False) -> dict:
    """YouTube da video qidiradi va ochadi"""
    try:
        encoded = urllib.parse.quote_plus(query)
        if autoplay:
            # To'g'ridan to'g'ri birinchi natijaga o'tish
            url = f"https://www.youtube.com/results?search_query={encoded}&sp=EgIQAQ%3D%3D"
        else:
            url = f"https://www.youtube.com/results?search_query={encoded}"

        result = open_url(url)
        if result["success"]:
            return {
                "success": True,
                "message": f"✅ YouTube da '{query}' qidiruvchi ochildi",
                "url": url,
                "tip": "Birinchi videoni bosib tomosha qilishingiz mumkin"
            }
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def play_youtube_music(song: str) -> dict:
    """YouTube Music da musiqa qidiradi"""
    try:
        encoded = urllib.parse.quote_plus(song + " official audio")
        url = f"https://music.youtube.com/search?q={encoded}"
        result = open_url(url)
        if result["success"]:
            return {
                "success": True,
                "message": f"✅ YouTube Music da '{song}' ochildi",
                "url": url
            }
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def open_instagram(username: str = None, search: str = None) -> dict:
    """Instagram ochadi"""
    try:
        if username:
            url = f"https://www.instagram.com/{username.lstrip('@')}/"
            msg = f"✅ Instagram da @{username} profili ochildi"
        elif search:
            encoded = urllib.parse.quote_plus(search)
            url = f"https://www.instagram.com/explore/tags/{encoded}/"
            msg = f"✅ Instagram da '{search}' qidiruvi ochildi"
        else:
            url = "https://www.instagram.com/"
            msg = "✅ Instagram ochildi"

        result = open_url(url)
        if result["success"]:
            return {"success": True, "message": msg, "url": url}
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def open_telegram_web() -> dict:
    """Telegram web ni brauzerda ochadi"""
    return open_url("https://web.telegram.org/")


def open_website(site: str) -> dict:
    """Istalgan saytni ochadi"""
    try:
        # URL ni to'g'rilash
        if not site.startswith(("http://", "https://")):
            # Oddiy sayt nomi (google, youtube, facebook...)
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
            if site.lower() in common:
                url = common[site.lower()]
            else:
                url = f"https://{site}" if "." in site else f"https://www.{site}.com"
        else:
            url = site

        result = open_url(url)
        if result["success"]:
            return {"success": True, "message": f"✅ Brauzerda ochildi: {url}", "url": url}
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_google(query: str) -> dict:
    """Google da qidiradi"""
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://www.google.com/search?q={encoded}"
        result = open_url(url)
        if result["success"]:
            return {
                "success": True,
                "message": f"✅ Google da '{query}' qidiruvi ochildi",
                "url": url
            }
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_youtube_video(query: str, category: str = None) -> dict:
    """
    YouTube da video qidiradi
    category: music, motivation, news, education, film
    """
    try:
        search_query = query
        if category == "music":
            search_query = f"{query} musiqa"
        elif category == "motivation":
            search_query = f"{query} motivatsiya video"
        elif category == "film":
            search_query = f"{query} to'liq kino"
        elif category == "news":
            search_query = f"{query} yangiliklar"

        encoded = urllib.parse.quote_plus(search_query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        result = open_url(url)
        if result["success"]:
            return {
                "success": True,
                "message": f"✅ YouTube da '{search_query}' videolari ochildi",
                "url": url,
                "izoh": "Brauzeringizda YouTube ochildi - istalgan videoni tanlang"
            }
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}
