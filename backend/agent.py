"""
Jarvis Agent - O'zbek tilida gaplashadigan AI Agent miyasi
Google Gemini API asosida - BARCHA toollar bilan
"""

import os
import json
import asyncio
import google.generativeai as genai

from tools.file_tools import (
    read_file, write_file, delete_file_tool, list_files,
    create_folder, copy_file, move_file, search_in_files, list_files_by_date
)
from tools.system_tools import (
    get_system_info, run_command, install_package, get_processes, clean_junk_files
)
from tools.code_tools import (
    analyze_code, generate_code, run_python_code
)
from tools.web_tools import search_web, fetch_url
from tools.weather_tools import get_weather
from tools.browser_tools import (
    open_website, search_youtube, search_youtube_video,
    play_youtube_music, open_instagram, search_google, open_telegram_web,
    browser_goto, browser_screenshot, browser_search_and_get, browser_youtube_play,
    browser_click_and_type
)
from tools.telegram_tools import get_messages, send_message, list_chats
from tools.remotion_tools import (
    render_text_video, render_slideshow,
    open_remotion_studio, list_rendered_videos
)
from tools.presentation_tools import create_presentation, list_presentations

SYSTEM_PROMPT = """Sen Jarvis — aqlli va qobiliyatli O'zbek AI agentisin.

QO'LLANUVCHAN QOIDALAR:
1. Har doim O'zbek tilida gapirasan — ravon, tabiiy, insoniy ohangda
2. Qisqa va aniq javob berasan, kerak bo'lsa batafsil tushuntirasan
3. Har qanday vazifani bajarasan: fayl boshqarish, kod yozish, paket o'rnatish,
   ob-havo bilish, YouTube/Instagram ochish, Telegram xabarlarini o'qish va yuborish
4. Xatolarni o'zing hal qilasan, foydalanuvchini bezovta qilmaysan
5. Ishni doimo oxiriga yetkizasan
6. "Men qila olmayman" dema — har doim yechim top!

QOBILIYATLARING:
📁 Fayllar     — yaratish, o'qish, o'chirish, nusxa, ko'chirish, qidirish
💻 Kod         — yozish, tahlil, ishga tushirish (Python)
⚙️  Sistema     — terminal buyruqlar, jarayonlar, paket o'rnatish
🌐 Internet    — qidirish, URL dan ma'lumot olish
🌤️  Ob-havo    — istalgan shahar, bugun/ertaga/indinga
📺 YouTube     — video/musiqa/kino/motivatsiya qidirish va ochish
📸 Instagram   — profil yoki teg bo'yicha ochish
🌍 Brauzer     — istalgan saytni ochish (Google, Telegram, va h.k.)
📱 Telegram    — chatlar, guruhlar, kanallar o'qish va xabar yuborish

MUHIM ESLATMALAR:
- Ob-havo so'ralganda: get_weather toolini ishlat
- YouTube/musiqa/kino so'ralganda: search_youtube_video yoki play_youtube_music ishlat
- Instagram so'ralganda: open_instagram ishlat
- Telegram xabar o'qish/yuborish: get_messages / send_message ishlat
- Sayt ochish: open_website ishlat
- Saytda harakatlanish kerak bo'lsa: browser_goto ishlat
- YouTube videoni haqiqiy o'ynatish: browser_youtube_play ishlat
- Sahifa screenshot: browser_screenshot ishlat
- Google/YouTube qidiruv natijalarini olish: browser_search_and_get ishlat
- Video render qilish: render_text_video ishlat
- Slayd video: render_slideshow ishlat
- Remotion Studio ochish: open_remotion_studio ishlat
- "Bugungi/kechagi fayllar" so'ralganda: list_files_by_date ishlat
- "Keraksiz fayllarni tozala" so'ralganda: clean_junk_files (avval dry_run=True, ko'rsatib, keyin dry_run=False)
- Prezentatsiya/taqdimot so'ralganda: create_presentation ishlat - slaydlarni o'zing to'liq mazmun bilan to'ldir"""



# ─── TOOL DEKLARATSIYALARI (Gemini uchun) ─────────────────────────────────────

def _obj(*props_required):
    """Yordamchi: object schema yaratadi"""
    props, required = props_required[0], props_required[1] if len(props_required) > 1 else []
    return genai.protos.Schema(
        type=genai.protos.Type.OBJECT,
        properties=props,
        required=required
    )

def _str(desc): return genai.protos.Schema(type=genai.protos.Type.STRING, description=desc)
def _int(desc): return genai.protos.Schema(type=genai.protos.Type.INTEGER, description=desc)
def _bool(desc): return genai.protos.Schema(type=genai.protos.Type.BOOLEAN, description=desc)

TOOL_DECLARATIONS = [genai.protos.Tool(function_declarations=[

    # ── FAYL TOOLLARI ──────────────────────────────────────────────────────────
    genai.protos.FunctionDeclaration(
        name="read_file",
        description="Faylni o'qiydi va mazmunini qaytaradi",
        parameters=_obj({"path": _str("Fayl yo'li")}, ["path"])
    ),
    genai.protos.FunctionDeclaration(
        name="write_file",
        description="Fayl yaratadi yoki yozadi",
        parameters=_obj({"path": _str("Fayl yo'li"), "content": _str("Yoziladigan mazmun")}, ["path", "content"])
    ),
    genai.protos.FunctionDeclaration(
        name="delete_file_tool",
        description="Fayl yoki papkani o'chiradi",
        parameters=_obj({"path": _str("O'chiriladigan fayl/papka yo'li")}, ["path"])
    ),
    genai.protos.FunctionDeclaration(
        name="list_files",
        description="Papka ichidagi fayllar ro'yxatini ko'rsatadi",
        parameters=_obj({"path": _str("Papka yo'li (ixtiyoriy)"), "recursive": _bool("Ichki papkalarni ham ko'rsatish")})
    ),
    genai.protos.FunctionDeclaration(
        name="create_folder",
        description="Yangi papka yaratadi",
        parameters=_obj({"path": _str("Yangi papka yo'li")}, ["path"])
    ),
    genai.protos.FunctionDeclaration(
        name="copy_file",
        description="Faylni nusxa oladi",
        parameters=_obj({"source": _str("Manba yo'li"), "destination": _str("Manzil yo'li")}, ["source", "destination"])
    ),
    genai.protos.FunctionDeclaration(
        name="move_file",
        description="Faylni ko'chiradi yoki nomini o'zgartiradi",
        parameters=_obj({"source": _str("Manba yo'li"), "destination": _str("Manzil yo'li")}, ["source", "destination"])
    ),
    genai.protos.FunctionDeclaration(
        name="search_in_files",
        description="Fayllar ichida matn qidiradi",
        parameters=_obj({"query": _str("Qidiriladigan matn"), "path": _str("Qidirish papkasi (ixtiyoriy)")}, ["query"])
    ),

    # ── SISTEMA TOOLLARI ───────────────────────────────────────────────────────
    genai.protos.FunctionDeclaration(
        name="get_system_info",
        description="Kompyuter haqida ma'lumot oladi: CPU, RAM, disk, OS",
        parameters=_obj({})
    ),
    genai.protos.FunctionDeclaration(
        name="run_command",
        description="Terminal/Shell da buyruq bajaradi",
        parameters=_obj({"command": _str("Bajariladigan buyruq"), "timeout": _int("Vaqt chegarasi soniyada")}, ["command"])
    ),
    genai.protos.FunctionDeclaration(
        name="install_package",
        description="pip yoki npm orqali paket o'rnatadi",
        parameters=_obj({"package": _str("Paket nomi"), "manager": _str("pip yoki npm")}, ["package"])
    ),
    genai.protos.FunctionDeclaration(
        name="get_processes",
        description="Ishlab turgan jarayonlar ro'yxatini ko'rsatadi",
        parameters=_obj({})
    ),

    # ── KOD TOOLLARI ──────────────────────────────────────────────────────────
    genai.protos.FunctionDeclaration(
        name="run_python_code",
        description="Python kodni bajaradi va natijani qaytaradi",
        parameters=_obj({"code": _str("Bajariladigan Python kodi")}, ["code"])
    ),
    genai.protos.FunctionDeclaration(
        name="analyze_code",
        description="Kodni tahlil qiladi, xatolar va tavsiyalarni topadi",
        parameters=_obj({"code": _str("Tahlil qilinadigan kod"), "language": _str("Dasturlash tili")}, ["code"])
    ),
    genai.protos.FunctionDeclaration(
        name="generate_code",
        description="Berilgan vazifa uchun kod yozadi va saqlaydi",
        parameters=_obj({"task": _str("Nima qilish kerak"), "language": _str("Dasturlash tili"), "save_path": _str("Saqlash yo'li (ixtiyoriy)")}, ["task", "language"])
    ),

    # ── INTERNET TOOLLARI ─────────────────────────────────────────────────────
    genai.protos.FunctionDeclaration(
        name="search_web",
        description="Internetdan ma'lumot qidiradi (DuckDuckGo)",
        parameters=_obj({"query": _str("Qidiruv so'rovi")}, ["query"])
    ),
    genai.protos.FunctionDeclaration(
        name="fetch_url",
        description="Web sahifadan mazmun oladi",
        parameters=_obj({"url": _str("To'liq URL manzil")}, ["url"])
    ),

    # ── OB-HAVO TOOLI ─────────────────────────────────────────────────────────
    genai.protos.FunctionDeclaration(
        name="get_weather",
        description="Shahar ob-havosini oladi: bugun, ertaga, indinga. Harorat, shamol, namlik, yog'ingarchilik.",
        parameters=_obj({"city": _str("Shahar nomi (masalan: Toshkent, Samarqand, London)"), "days": _int("Necha kunlik prognoz: 1=bugun, 2=ertaga, 3=indinga")}, ["city"])
    ),

    # ── BRAUZER / WEB OCHISH TOOLLARI ─────────────────────────────────────────
    genai.protos.FunctionDeclaration(
        name="open_website",
        description="Brauzerda istalgan saytni ochadi (youtube, instagram, telegram, google va h.k.)",
        parameters=_obj({"site": _str("Sayt nomi yoki URL (masalan: youtube, instagram, google.com)")}, ["site"])
    ),
    genai.protos.FunctionDeclaration(
        name="search_youtube_video",
        description="YouTube da video qidiradi va brauzerda ochadi. Musiqa, kino, motivatsiya, yangiliklar uchun.",
        parameters=_obj({"query": _str("Qidiriladigan video nomi yoki mavzu"), "category": _str("Kategoriya: music, motivation, film, news, education (ixtiyoriy)")}, ["query"])
    ),
    genai.protos.FunctionDeclaration(
        name="play_youtube_music",
        description="YouTube Music da musiqa qidiradi va ochadi",
        parameters=_obj({"song": _str("Qo'shiq yoki artist nomi")}, ["song"])
    ),
    genai.protos.FunctionDeclaration(
        name="open_instagram",
        description="Instagram ochadi: profil, hashtag yoki asosiy sahifa",
        parameters=_obj({"username": _str("Instagram foydalanuvchi nomi @ bilan (ixtiyoriy)"), "search": _str("Hashtag yoki qidiruv (ixtiyoriy)")})
    ),
    genai.protos.FunctionDeclaration(
        name="search_google",
        description="Google da qidiradi va brauzerda ochadi",
        parameters=_obj({"query": _str("Qidiruv so'rovi")}, ["query"])
    ),
    genai.protos.FunctionDeclaration(
        name="open_telegram_web",
        description="Telegram web ni brauzerda ochadi",
        parameters=_obj({})
    ),

    # ── PLAYWRIGHT BROWSER AUTOMATION ─────────────────────────────────────────
    genai.protos.FunctionDeclaration(
        name="browser_goto",
        description="Playwright bilan berilgan URL ga kiradi, sahifa mazmunini qaytaradi. Saytda haqiqiy kirish kerak bo'lganda ishlat.",
        parameters=_obj({
            "url": _str("To'liq URL (https://...)"),
            "wait_seconds": _int("Sahifa yuklangandan keyin kutish vaqti (standart: 3)")
        }, ["url"])
    ),
    genai.protos.FunctionDeclaration(
        name="browser_screenshot",
        description="Sahifaning screenshot ini oladi va workspace ga saqlaydi",
        parameters=_obj({"url": _str("Screenshot olinadigan sahifa URL")}, ["url"])
    ),
    genai.protos.FunctionDeclaration(
        name="browser_search_and_get",
        description="Google yoki YouTube da qidiradi, natijalarni qaytaradi va brauzerda ochadi",
        parameters=_obj({
            "query": _str("Qidiruv so'rovi"),
            "engine": _str("Qidiruv tizimi: google yoki youtube (standart: google)")
        }, ["query"])
    ),
    genai.protos.FunctionDeclaration(
        name="browser_youtube_play",
        description="YouTube da video topadi va birinchi natijani haqiqiy o'ynatadi (brauzer ochilib video boshlanadi)",
        parameters=_obj({"query": _str("Video, qo'shiq yoki mavzu nomi")}, ["query"])
    ),
    genai.protos.FunctionDeclaration(
        name="browser_click_and_type",
        description="Saytdagi input maydoniga bosib matn yozadi (forma to'ldirish uchun)",
        parameters=_obj({
            "url": _str("Sahifa URL"),
            "selector": _str("CSS selector (masalan: input[name=q], #search)"),
            "text": _str("Yoziladigan matn")
        }, ["url", "selector", "text"])
    ),

    # ── TELEGRAM TOOLLARI ─────────────────────────────────────────────────────
    genai.protos.FunctionDeclaration(
        name="get_messages",
        description="Telegram chatdan xabarlarni o'qiydi. chat ko'rsatilmasa barcha dialoglarni ko'rsatadi.",
        parameters=_obj({"chat": _str("Chat nomi, username yoki ID (ixtiyoriy, bo'sh qolsa barcha dialoglar)"), "limit": _int("Nechta xabar (standart: 10)")})
    ),
    genai.protos.FunctionDeclaration(
        name="send_message",
        description="Telegram orqali xabar yuboradi",
        parameters=_obj({"chat": _str("Chat username yoki nomi"), "text": _str("Yuborilishi kerak bo'lgan xabar matni")}, ["chat", "text"])
    ),
    genai.protos.FunctionDeclaration(
        name="list_chats",
        description="Barcha Telegram chatlar, guruhlar, kanallar va botlarni ko'rsatadi",
        parameters=_obj({"limit": _int("Ko'rsatiladigan chat soni (standart: 20)")})
    ),

    # ── REMOTION VIDEO RENDER ─────────────────────────────────────────────────
    genai.protos.FunctionDeclaration(
        name="render_text_video",
        description="Matn bilan professional video render qiladi (MP4). Taqdimot, reklama, motivatsiya videolari uchun.",
        parameters=_obj({
            "text":             _str("Videoda ko'rsatiladigan matn"),
            "output_filename":  _str("Fayl nomi (masalan: video.mp4)"),
            "bg_color":         _str("Fon rangi hex formatda (masalan: #0a0a0f)"),
            "text_color":       _str("Matn rangi hex formatda (masalan: #4f8ef7)"),
            "duration_seconds": _int("Video davomiyligi soniyalarda (standart: 5)"),
            "fps":              _int("Kadrlar soni (standart: 30)")
        }, ["text"])
    ),
    genai.protos.FunctionDeclaration(
        name="render_slideshow",
        description="Bir necha slayddan iborat video yaratadi",
        parameters=_obj({
            "slides":           _str("Slaydlar ro'yxati JSON formatda: [{\"text\":\"...\", \"bg_color\":\"#...\"}]"),
            "output_filename":  _str("Fayl nomi (masalan: slideshow.mp4)"),
            "slide_duration":   _int("Har bir slayd davomiyligi soniyalarda (standart: 3)")
        }, ["slides"])
    ),
    genai.protos.FunctionDeclaration(
        name="open_remotion_studio",
        description="Remotion Studio ni ochadi — videoni vizual tahrirlash uchun brauzer interfeysi",
        parameters=_obj({})
    ),
    genai.protos.FunctionDeclaration(
        name="list_rendered_videos",
        description="Workspace da render qilingan barcha videolar ro'yxatini ko'rsatadi",
        parameters=_obj({})
    ),

    # ── SANA BO'YICHA FAYLLAR ─────────────────────────────────────────────────
    genai.protos.FunctionDeclaration(
        name="list_files_by_date",
        description="Sana bo'yicha fayllarni topadi (o'zgartirilgan vaqti bo'yicha). Bugun/kecha/oxirgi hafta yaratilgan yoki o'zgartirilgan fayllarni ko'rsatadi.",
        parameters=_obj({
            "when": _str("Davr: today (bugun), yesterday (kecha), week (oxirgi hafta)"),
            "folder": _str("Qidirish papkasi (ixtiyoriy, bo'sh bo'lsa asosiy papkalar)"),
            "extension": _str("Faqat shu kengaytma, masalan .pdf .jpg (ixtiyoriy)")
        })
    ),

    # ── KERAKSIZ FAYLLARNI TOZALASH ───────────────────────────────────────────
    genai.protos.FunctionDeclaration(
        name="clean_junk_files",
        description="Keraksiz vaqtinchalik (temp/cache) fayllarni tozalaydi. XAVFSIZ - faqat tizim temp papkalari. Avval dry_run=True bilan hisoblang, keyin dry_run=False bilan o'chiring.",
        parameters=_obj({
            "dry_run": _bool("True - faqat hisoblaydi (o'chirmaydi), False - haqiqatan o'chiradi")
        })
    ),

    # ── PREZENTATSIYA YARATISH ────────────────────────────────────────────────
    genai.protos.FunctionDeclaration(
        name="create_presentation",
        description="Professional PowerPoint (.pptx) prezentatsiya yaratadi. Slaydlarni mavzu bo'yicha to'ldiradi.",
        parameters=_obj({
            "title": _str("Prezentatsiya sarlavhasi"),
            "slides": _str("Slaydlar JSON ro'yxati: [{\"heading\":\"Sarlavha\",\"points\":[\"fikr1\",\"fikr2\"]}]"),
            "output_filename": _str("Fayl nomi (masalan: taqdimot.pptx)"),
            "theme": _str("Dizayn: dark, light, ocean, sunset, emerald")
        }, ["title", "slides"])
    ),
    genai.protos.FunctionDeclaration(
        name="list_presentations",
        description="Yaratilgan prezentatsiyalar ro'yxatini ko'rsatadi",
        parameters=_obj({})
    ),

])]



# ─── TOOL MAP: nom → funksiya ─────────────────────────────────────────────────

TOOL_MAP = {
    # Fayl
    "read_file": read_file,
    "write_file": write_file,
    "delete_file_tool": delete_file_tool,
    "list_files": list_files,
    "create_folder": create_folder,
    "copy_file": copy_file,
    "move_file": move_file,
    "search_in_files": search_in_files,
    # Sistema
    "get_system_info": get_system_info,
    "run_command": run_command,
    "install_package": install_package,
    "get_processes": get_processes,
    # Kod
    "run_python_code": run_python_code,
    "analyze_code": analyze_code,
    "generate_code": generate_code,
    # Internet
    "search_web": search_web,
    "fetch_url": fetch_url,
    # Ob-havo
    "get_weather": get_weather,
    # Brauzer
    "open_website": open_website,
    "search_youtube_video": search_youtube_video,
    "play_youtube_music": play_youtube_music,
    "open_instagram": open_instagram,
    "search_google": search_google,
    "open_telegram_web": open_telegram_web,
    # Playwright browser automation
    "browser_goto": browser_goto,
    "browser_screenshot": browser_screenshot,
    "browser_search_and_get": browser_search_and_get,
    "browser_youtube_play": browser_youtube_play,
    "browser_click_and_type": browser_click_and_type,
    # Telegram
    "get_messages": get_messages,
    "send_message": send_message,
    "list_chats": list_chats,
    # Remotion video render
    "render_text_video":    render_text_video,
    "render_slideshow":     render_slideshow,
    "open_remotion_studio": open_remotion_studio,
    "list_rendered_videos": list_rendered_videos,
    # Sana bo'yicha fayllar
    "list_files_by_date":   list_files_by_date,
    # Keraksiz fayllarni tozalash
    "clean_junk_files":     clean_junk_files,
    # Prezentatsiya
    "create_presentation":  create_presentation,
    "list_presentations":   list_presentations,
}


# ─── JARVIS AGENT KLASSI ──────────────────────────────────────────────────────

# Sinab ko'riladigan modellar (yangi → eski tartibda)
# Birinchi ishlaydigani tanlanadi. Har bir modelda alohida bepul kvota bor.
CANDIDATE_MODELS = [
    "gemini-3.5-flash",        # so'ralgan (mavjud bo'lsa)
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.0-flash-001",
    "gemini-flash-latest",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-flash-8b",
]


def _load_api_keys() -> list:
    """.env dan barcha API kalitlarni yig'adi (primary + zaxira)"""
    keys = []
    for var in ("GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"):
        val = os.getenv(var, "").strip()
        if val and val not in keys and "your_" not in val:
            keys.append(val)
    return keys


def _list_available_models() -> list:
    """API dan generateContent qo'llab-quvvatlaydigan modellar ro'yxati"""
    try:
        available = []
        for m in genai.list_models():
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                available.append(m.name.replace("models/", ""))
        return available
    except Exception as e:
        print(f"[Gemini] Model ro'yxatini olishda xato: {e}")
        return []


def _pick_working_model() -> str:
    """Mavjud modellardan ishlaydiganini avtomatik tanlaydi (validatsiya bilan)"""
    available = _list_available_models()
    env_model = os.getenv("GEMINI_MODEL", "").strip()

    # .env da model ko'rsatilgan va u haqiqatan mavjud bo'lsa — o'shani ishlat
    if env_model:
        if not available or env_model in available:
            print(f"[Gemini] Model (.env): {env_model}")
            return env_model
        print(f"[Gemini] '{env_model}' mavjud emas, avtomatik tanlanmoqda...")

    # Nomzodlar ichidan birinchi mavjudini tanlash
    for cand in CANDIDATE_MODELS:
        if not available or cand in available:
            if available:
                print(f"[Gemini] Model tanlandi: {cand}")
                return cand
    # Ro'yxatdan flash modelni topish
    for name in available:
        if "flash" in name:
            print(f"[Gemini] Model tanlandi (avto): {name}")
            return name
    if available:
        return available[0]
    return "gemini-2.0-flash"


class JarvisAgent:
    def __init__(self):
        self.api_keys = _load_api_keys()
        if not self.api_keys:
            raise ValueError("GEMINI_API_KEY topilmadi! .env faylini tekshiring.")
        self.key_idx = 0
        genai.configure(api_key=self.api_keys[self.key_idx])

        self.model_name = _pick_working_model()
        # 429 bo'lsa almashish uchun zaxira modellar ro'yxati
        self.fallback_models = [m for m in CANDIDATE_MODELS if m != self.model_name]
        self._build_model(self.model_name)
        self.chat = self.model.start_chat(history=[])

    def _build_model(self, name):
        self.model = genai.GenerativeModel(
            model_name=name,
            tools=TOOL_DECLARATIONS,
            system_instruction=SYSTEM_PROMPT
        )

    def reset_conversation(self):
        self.chat = self.model.start_chat(history=[])

    def _rebuild_with_model(self, new_model_name: str):
        """Modelni almashtiradi, suhbat tarixini saqlab qoladi"""
        try:
            history = self.chat.history
        except Exception:
            history = []
        self.model_name = new_model_name
        self._build_model(new_model_name)
        self.chat = self.model.start_chat(history=history)
        print(f"[Gemini] Modelga o'tildi: {new_model_name}")

    def _switch_api_key(self) -> bool:
        """Keyingi API kalitga o'tadi. Muvaffaqiyatli bo'lsa True."""
        if self.key_idx + 1 >= len(self.api_keys):
            return False
        try:
            history = self.chat.history
        except Exception:
            history = []
        self.key_idx += 1
        genai.configure(api_key=self.api_keys[self.key_idx])
        self._build_model(self.model_name)
        self.chat = self.model.start_chat(history=history)
        print(f"[Gemini] Zaxira API kalitga o'tildi (#{self.key_idx + 1})")
        return True

    async def _send(self, message, on_step=None):
        """
        Xabar yuboradi. Xatolarda avtomatik tiklanadi:
        1. 429/quota yoki 404 → boshqa modelga o'tadi (har modelda alohida kvota)
        2. Barcha modellar tugasa → zaxira API kalitga o'tadi
        3. Hammasi tugasa → biroz kutib qayta urinadi
        """
        import re as _re
        tried_models = []
        max_attempts = (len(self.fallback_models) + 2) * max(1, len(self.api_keys)) + 2
        for attempt in range(max_attempts):
            try:
                return await asyncio.to_thread(self.chat.send_message, message)
            except Exception as e:
                err = str(e)
                low = err.lower()
                is_quota = "429" in err or "quota" in low or "exhausted" in low or "resource" in low
                is_notfound = "404" in err or "not found" in low or "not supported" in low
                if not (is_quota or is_notfound):
                    raise  # boshqa xato (masalan auth) — yuqoriga uzatamiz

                tried_models.append(self.model_name)
                next_model = next((m for m in self.fallback_models if m not in tried_models), None)

                if next_model:
                    if on_step:
                        msg = "topilmadi" if is_notfound else "kvota tugadi"
                        await on_step(f"⚠️ {self.model_name} {msg}, {next_model} ga o'tilmoqda...")
                    self._rebuild_with_model(next_model)
                    continue

                # Barcha modellar tugagan → zaxira kalitga o'tish
                if self._switch_api_key():
                    if on_step:
                        await on_step("🔑 Zaxira API kalitga o'tilmoqda...")
                    tried_models = []
                    self._rebuild_with_model(CANDIDATE_MODELS[0])
                    self.fallback_models = [m for m in CANDIDATE_MODELS if m != self.model_name]
                    continue

                # Kalitlar ham tugadi — kutish
                if is_quota:
                    m = _re.search(r"retry.*?(\d+)", err)
                    wait = min(int(m.group(1)) if m else 30, 60)
                    if on_step:
                        await on_step(f"⏳ Barcha kalitlar band. {wait}s kutilmoqda...")
                    await asyncio.sleep(wait)
                    tried_models = []
                    self.key_idx = 0
                    genai.configure(api_key=self.api_keys[0])
                    self._rebuild_with_model(CANDIDATE_MODELS[0])
                    self.fallback_models = [m for m in CANDIDATE_MODELS if m != self.model_name]
                else:
                    break
        raise RuntimeError(
            "Barcha Gemini modellari va kalitlarining kvotasi tugagan yoki model topilmadi. "
            "Iltimos bir necha daqiqa kuting yoki yangi API kalit kiriting."
        )

    async def think_and_act(self, user_message: str, on_step=None) -> str:
        """
        Agent fikrlaydi → toollarni chaqiradi → javob beradi
        Maksimum 10 qadam (loop himoyasi)
        """
        max_iterations = 10
        iteration = 0

        # Foydalanuvchi xabarini yubor (429 da avtomatik model almashadi)
        response = await self._send(user_message, on_step=on_step)

        while iteration < max_iterations:
            iteration += 1

            # Tool chaqiruvlarini yig'ish
            tool_calls = [
                part.function_call
                for part in response.parts
                if hasattr(part, "function_call") and part.function_call.name
            ]

            # Tool yo'q → oxirgi matn javob
            if not tool_calls:
                text = "".join(
                    part.text for part in response.parts
                    if hasattr(part, "text") and part.text
                )
                return text.strip() or "✅ Bajarildi."

            # Toollarni parallel bajarish
            tool_responses = []
            for fc in tool_calls:
                func_name = fc.name
                args = dict(fc.args)

                if on_step:
                    step_labels = {
                        "get_weather": "🌤️ Ob-havo tekshirilmoqda...",
                        "search_youtube_video": "📺 YouTube qidirilmoqda...",
                        "play_youtube_music": "🎵 Musiqa qidirilmoqda...",
                        "open_instagram": "📸 Instagram ochilmoqda...",
                        "open_website": "🌐 Sayt ochilmoqda...",
                        "get_messages": "📱 Telegram xabarlar o'qilmoqda...",
                        "send_message": "📤 Telegram xabar yuborilmoqda...",
                        "list_chats": "💬 Telegram chatlar yuklanmoqda...",
                        "read_file": "📄 Fayl o'qilmoqda...",
                        "write_file": "💾 Fayl saqlanmoqda...",
                        "run_command": "⚙️ Buyruq bajarilmoqda...",
                        "run_python_code": "🐍 Python kodi ishga tushirilmoqda...",
                        "install_package": "📦 Paket o'rnatilmoqda...",
                        "search_web": "🔍 Internet qidirilmoqda...",
                        "get_system_info": "💻 Sistema ma'lumoti olinmoqda...",
                        "browser_goto": "🌐 Brauzer sahifasi ochilmoqda...",
                        "browser_screenshot": "📸 Screenshot olinmoqda...",
                        "browser_search_and_get": "🔍 Brauzer qidiruvi bajarilmoqda...",
                        "browser_youtube_play": "▶️ YouTube video o'ynatilmoqda...",
                        "browser_click_and_type": "⌨️ Brauzerda matn yozilmoqda...",
                        "render_text_video":    "🎬 Video render qilinmoqda...",
                        "render_slideshow":     "🎞️ Slaydshow render qilinmoqda...",
                        "open_remotion_studio": "🎨 Remotion Studio ochilmoqda...",
                        "list_rendered_videos": "📹 Videolar ro'yxati olinmoqda...",
                        "list_files_by_date":   "🗓️ Sana bo'yicha fayllar qidirilmoqda...",
                        "clean_junk_files":     "🧹 Keraksiz fayllar tozalanmoqda...",
                        "create_presentation":  "📊 Prezentatsiya tayyorlanmoqda...",
                        "list_presentations":   "📑 Prezentatsiyalar ro'yxati...",
                    }
                    label = step_labels.get(func_name, f"🔧 {func_name} bajarilmoqda...")
                    await on_step(label)

                # Funksiyani chaqirish
                if func_name in TOOL_MAP:
                    try:
                        func = TOOL_MAP[func_name]
                        if asyncio.iscoroutinefunction(func):
                            result = await func(**args)
                        else:
                            result = await asyncio.to_thread(func, **args)
                        result_str = json.dumps(result, ensure_ascii=False) if isinstance(result, dict) else str(result)
                    except Exception as e:
                        result_str = json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
                else:
                    result_str = json.dumps({"success": False, "error": f"Noma'lum tool: {func_name}"})

                tool_responses.append(
                    genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(
                            name=func_name,
                            response={"result": result_str}
                        )
                    )
                )

            # Tool natijalarini modelga yubor
            response = await asyncio.to_thread(
                self.chat.send_message,
                genai.protos.Content(parts=tool_responses, role="user")
            )

        return "⚠️ Kechirasiz, vazifani bajarishda muammo yuz berdi. Iltimos qaytadan urinib ko'ring."
