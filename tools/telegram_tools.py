"""
Telegram toollari - xabarlar o'qish, yuborish, guruhlar, kanallar
Telethon kutubxonasi ishlatiladi (foydalanuvchi akkaunti sifatida kirish)
"""

import os
import json
import asyncio

# Telegram credentials .env dan olinadi
TG_API_ID = os.getenv("TELEGRAM_API_ID", "")
TG_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
TG_PHONE = os.getenv("TELEGRAM_PHONE", "")
SESSION_FILE = os.path.join(os.path.dirname(__file__), "../memory/telegram_session")


def _get_client():
    """Telethon client yaratadi"""
    try:
        from telethon import TelegramClient
        return TelegramClient(SESSION_FILE, int(TG_API_ID), TG_API_HASH)
    except ImportError:
        return None
    except Exception:
        return None


def get_messages(chat: str = None, limit: int = 10) -> dict:
    """Telegram chatdan oxirgi xabarlarni o'qiydi"""
    if not TG_API_ID or not TG_API_HASH:
        return {
            "success": False,
            "error": "Telegram API sozlanmagan. .env ga TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE qo'shing",
            "setup_url": "https://my.telegram.org/apps"
        }

    async def _fetch():
        from telethon import TelegramClient
        from telethon.tl.types import User, Channel, Chat
        async with TelegramClient(SESSION_FILE, int(TG_API_ID), TG_API_HASH) as client:
            messages = []
            if chat:
                entity = await client.get_entity(chat)
                async for msg in client.iter_messages(entity, limit=limit):
                    sender_name = "Noma'lum"
                    if msg.sender:
                        if hasattr(msg.sender, 'first_name'):
                            sender_name = (msg.sender.first_name or "") + " " + (msg.sender.last_name or "")
                        elif hasattr(msg.sender, 'title'):
                            sender_name = msg.sender.title
                    messages.append({
                        "id": msg.id,
                        "sender": sender_name.strip(),
                        "text": msg.text or "[media/file]",
                        "date": str(msg.date)[:16],
                        "is_outgoing": msg.out
                    })
            else:
                # Barcha dialoglardan oxirgi xabarlar
                async for dialog in client.iter_dialogs(limit=limit):
                    messages.append({
                        "name": dialog.name,
                        "type": "kanal" if dialog.is_channel else ("guruh" if dialog.is_group else "shaxsiy"),
                        "unread": dialog.unread_count,
                        "last_message": dialog.message.text[:80] if dialog.message and dialog.message.text else "[media]",
                        "date": str(dialog.date)[:16]
                    })
            return messages

    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(_fetch())
        loop.close()
        label = f"'{chat}' chatidan" if chat else "barcha dialoglar"
        return {"success": True, "source": label, "count": len(result), "messages": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def send_message(chat: str, text: str) -> dict:
    """Telegram ga xabar yuboradi"""
    if not TG_API_ID or not TG_API_HASH:
        return {"success": False, "error": "Telegram API sozlanmagan"}

    async def _send():
        from telethon import TelegramClient
        async with TelegramClient(SESSION_FILE, int(TG_API_ID), TG_API_HASH) as client:
            await client.send_message(chat, text)

    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(_send())
        loop.close()
        return {"success": True, "message": f"✅ '{chat}' ga xabar yuborildi: {text[:50]}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_chats(limit: int = 20) -> dict:
    """Barcha chatlar, guruhlar, kanallar ro'yxati"""
    if not TG_API_ID or not TG_API_HASH:
        return {"success": False, "error": "Telegram API sozlanmagan"}

    async def _list():
        from telethon import TelegramClient
        result = {"shaxsiy": [], "guruhlar": [], "kanallar": [], "botlar": []}
        async with TelegramClient(SESSION_FILE, int(TG_API_ID), TG_API_HASH) as client:
            async for dialog in client.iter_dialogs(limit=limit):
                item = {"name": dialog.name, "id": dialog.id, "unread": dialog.unread_count}
                if dialog.is_channel:
                    result["kanallar"].append(item)
                elif dialog.is_group:
                    result["guruhlar"].append(item)
                else:
                    entity = dialog.entity
                    if hasattr(entity, 'bot') and entity.bot:
                        result["botlar"].append(item)
                    else:
                        result["shaxsiy"].append(item)
        return result

    try:
        loop = asyncio.new_event_loop()
        chats = loop.run_until_complete(_list())
        loop.close()
        total = sum(len(v) for v in chats.values())
        return {"success": True, "total": total, "chats": chats}
    except Exception as e:
        return {"success": False, "error": str(e)}
