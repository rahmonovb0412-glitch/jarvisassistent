"""
Internet qidirish va ma'lumot olish toollari
"""

import requests
import re
from urllib.parse import urlencode, quote_plus


def search_web(query: str) -> dict:
    """DuckDuckGo orqali internetdan qidiradi"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        # DuckDuckGo Instant Answer API (bepul, kalit kerak emas)
        params = {
            "q": query,
            "format": "json",
            "no_redirect": "1",
            "no_html": "1",
            "skip_disambig": "1"
        }
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params=params,
            headers=headers,
            timeout=10
        )
        data = resp.json()

        results = []

        # Abstract
        if data.get("AbstractText"):
            results.append({
                "title": data.get("Heading", ""),
                "snippet": data["AbstractText"],
                "url": data.get("AbstractURL", "")
            })

        # Related topics
        for topic in data.get("RelatedTopics", [])[:5]:
            if isinstance(topic, dict) and topic.get("Text"):
                results.append({
                    "title": topic.get("Text", "")[:100],
                    "snippet": topic.get("Text", ""),
                    "url": topic.get("FirstURL", "")
                })

        if not results:
            return {
                "success": True,
                "query": query,
                "message": "Natija topilmadi. URL orqali to'g'ridan qidiring.",
                "results": []
            }

        return {
            "success": True,
            "query": query,
            "found": len(results),
            "results": results
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def fetch_url(url: str) -> dict:
    """Web sahifadan matn ma'lumot oladi"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        # HTML taglarini olib tashlash
        text = resp.text
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return {
            "success": True,
            "url": url,
            "status_code": resp.status_code,
            "content": text[:5000],  # Dastlabki 5000 belgi
            "content_length": len(text)
        }
    except requests.exceptions.Timeout:
        return {"success": False, "error": "So'rov vaqti tugadi (timeout)"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Internet aloqasi yo'q yoki URL noto'g'ri"}
    except Exception as e:
        return {"success": False, "error": str(e)}
