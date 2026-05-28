"""
Ob-havo toollari - wttr.in (bepul, API kalit kerak emas)
"""

import requests
import json


def get_weather(city: str, days: int = 1) -> dict:
    """
    Shahar ob-havosini oladi
    wttr.in - bepul, API kalit kerak emas
    days: 1=bugun, 2=ertaga, 3=indinga
    """
    try:
        # O'zbek shaharlari uchun inglizcha nomlar
        city_map = {
            "toshkent": "Tashkent",
            "samarqand": "Samarkand",
            "buxoro": "Bukhara",
            "namangan": "Namangan",
            "andijon": "Andijan",
            "farg'ona": "Fergana",
            "fargona": "Fergana",
            "nukus": "Nukus",
            "qarshi": "Karshi",
            "termiz": "Termez",
            "navoiy": "Navoiy",
            "jizzax": "Jizzakh",
            "urganch": "Urgench",
            "moskva": "Moscow",
            "london": "London",
            "dubai": "Dubai",
            "istanbul": "Istanbul",
        }
        query_city = city_map.get(city.lower(), city)

        url = f"https://wttr.in/{query_city}?format=j1&lang=uz"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        results = []
        weather_codes = {
            "113": "☀️ Quyoshli",
            "116": "⛅ Qisman bulutli",
            "119": "☁️ Bulutli",
            "122": "☁️ Qoʻngʻir bulut",
            "143": "🌫️ Tuman",
            "176": "🌦️ Ba'zan yomgʻir",
            "185": "🌧️ Qirov yomgʻir",
            "200": "⛈️ Momaqaldiroq",
            "227": "🌨️ Qor boʻroni",
            "230": "❄️ Qattiq qor boʻroni",
            "248": "🌫️ Qalin tuman",
            "260": "🌫️ Muzli tuman",
            "263": "🌦️ Yengil shashala yomgʻir",
            "266": "🌧️ Yengil yomgʻir",
            "281": "🌧️ Muzli yomgʻir",
            "293": "🌦️ Yengil yomgʻir",
            "296": "🌧️ Yomgʻir",
            "299": "🌧️ Oʻrtacha yomgʻir",
            "302": "🌧️ Kuchli yomgʻir",
            "305": "🌧️ Juda kuchli yomgʻir",
            "308": "⛈️ Juda kuchli yomgʻir",
            "311": "🌧️ Muzli shashala",
            "314": "🌧️ Muzli yomgʻir",
            "317": "🌨️ Yengil qor-yomgʻir",
            "320": "🌨️ Oʻrtacha qor-yomgʻir",
            "323": "🌨️ Yengil qor",
            "326": "❄️ Oʻrtacha qor",
            "329": "❄️ Kuchli qor",
            "332": "❄️ Juda kuchli qor",
            "335": "❄️ Qor boʻroni",
            "338": "❄️ Juda kuchli qor",
            "350": "🌧️ Muzli yomgʻir",
            "353": "🌦️ Yengil yomgʻir",
            "356": "🌧️ Kuchli yomgʻir",
            "359": "⛈️ Juda kuchli yomgʻir",
            "362": "🌨️ Yengil qor-yomgʻir",
            "365": "🌨️ Kuchli qor-yomgʻir",
            "368": "❄️ Yengil qor",
            "371": "❄️ Kuchli qor",
            "374": "🌨️ Muzli yomgʻir donalari",
            "377": "🌨️ Qor donalari",
            "386": "⛈️ Momaqaldiroqli yomgʻir",
            "389": "⛈️ Kuchli momaqaldiroqli yomgʻir",
            "392": "⛈️ Momaqaldiroqli qor",
            "395": "⛈️ Kuchli momaqaldiroqli qor",
        }

        day_names = ["Bugun", "Ertaga", "Indinga"]
        max_days = min(days, 3)

        for i in range(max_days):
            if i >= len(data.get("weather", [])):
                break
            day = data["weather"][i]
            code = day.get("weatherCode", "113")
            condition = weather_codes.get(str(code), "🌤️ Aniqlanmadi")

            max_c = day.get("maxtempC", "?")
            min_c = day.get("mintempC", "?")
            avg_c = day.get("avgtempC", "?")
            rain_mm = day.get("totalSnow_cm", "0")
            sun_hours = day.get("sunHour", "?")
            uv = day.get("uvIndex", "?")

            # Shamol
            hourly = day.get("hourly", [])
            wind_speeds = [int(h.get("windspeedKmph", 0)) for h in hourly]
            avg_wind = sum(wind_speeds) // len(wind_speeds) if wind_speeds else 0

            results.append({
                "kun": day_names[i] if i < len(day_names) else f"{i+1}-kun",
                "holat": condition,
                "harorat": f"Min: {min_c}°C | O'rtacha: {avg_c}°C | Max: {max_c}°C",
                "shamol": f"{avg_wind} km/soat",
                "quyosh_soati": f"{sun_hours} soat",
                "uv_indeks": str(uv),
                "yomgir_qor": f"{rain_mm} mm" if float(rain_mm or 0) > 0 else "Yo'q"
            })

        # Hozirgi holat
        current = data.get("current_condition", [{}])[0]
        current_temp = current.get("temp_C", "?")
        feels_like = current.get("FeelsLikeC", "?")
        humidity = current.get("humidity", "?")
        visibility = current.get("visibility", "?")
        current_code = current.get("weatherCode", "113")
        current_condition = weather_codes.get(str(current_code), "🌤️")

        return {
            "success": True,
            "shahar": query_city,
            "hozir": {
                "holat": current_condition,
                "harorat": f"{current_temp}°C (his qilinadi: {feels_like}°C)",
                "namlik": f"{humidity}%",
                "korinish": f"{visibility} km"
            },
            "prognoz": results
        }

    except requests.exceptions.Timeout:
        return {"success": False, "error": "Internet ulanish vaqti tugadi"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Internet aloqasi yo'q"}
    except Exception as e:
        return {"success": False, "error": f"Ob-havo ma'lumoti olinmadi: {str(e)}"}


def get_weather_simple(city: str) -> str:
    """Sodda matn formatida ob-havo"""
    result = get_weather(city, days=2)
    if not result["success"]:
        return f"❌ {result['error']}"

    lines = [f"🌍 {result['shahar']} ob-havosi:\n"]
    h = result["hozir"]
    lines.append(f"Hozir: {h['holat']} {h['harorat']}")
    lines.append(f"Namlik: {h['namlik']} | Ko'rinish: {h['korinish']}\n")

    for p in result["prognoz"]:
        lines.append(f"📅 {p['kun']}: {p['holat']}")
        lines.append(f"   🌡️ {p['harorat']}")
        lines.append(f"   💨 Shamol: {p['shamol']}")
        if p['yomgir_qor'] != "Yo'q":
            lines.append(f"   🌧️ Yog'ingarchilik: {p['yomgir_qor']}")
        lines.append("")

    return "\n".join(lines)
