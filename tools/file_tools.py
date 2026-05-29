"""
Fayl boshqarish toollari - o'qish, yozish, o'chirish, ko'chirish
"""

import os
import shutil
import glob


WORKSPACE = os.getenv("WORKSPACE_DIR", "./workspace")


def _safe_path(path: str) -> str:
    """Xavfsiz yo'l - workspace ichida"""
    if os.path.isabs(path):
        return path
    return os.path.join(WORKSPACE, path)


def read_file(path: str) -> dict:
    """Faylni o'qiydi"""
    try:
        full_path = _safe_path(path)
        if not os.path.exists(full_path):
            return {"success": False, "error": f"Fayl topilmadi: {path}"}
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        size = os.path.getsize(full_path)
        return {
            "success": True,
            "path": full_path,
            "content": content,
            "size": f"{size} bayt",
            "lines": content.count('\n') + 1
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def write_file(path: str, content: str) -> dict:
    """Fayl yaratadi yoki yozadi"""
    try:
        full_path = _safe_path(path)
        # Papkalarni avtomatik yaratish
        os.makedirs(os.path.dirname(full_path) if os.path.dirname(full_path) else ".", exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        return {
            "success": True,
            "message": f"✅ Fayl saqlandi: {path}",
            "path": full_path,
            "size": f"{len(content.encode('utf-8'))} bayt"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_file_tool(path: str) -> dict:
    """Fayl yoki papkani o'chiradi"""
    try:
        full_path = _safe_path(path)
        if not os.path.exists(full_path):
            return {"success": False, "error": f"Topilmadi: {path}"}
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
            return {"success": True, "message": f"✅ Papka o'chirildi: {path}"}
        else:
            os.remove(full_path)
            return {"success": True, "message": f"✅ Fayl o'chirildi: {path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_files(path: str = None, recursive: bool = False) -> dict:
    """Fayllar ro'yxatini qaytaradi"""
    try:
        target = _safe_path(path) if path else WORKSPACE
        if not os.path.exists(target):
            os.makedirs(target, exist_ok=True)
            return {"success": True, "files": [], "message": "Papka bo'sh"}

        items = []
        if recursive:
            for root, dirs, files in os.walk(target):
                for d in dirs:
                    rel = os.path.relpath(os.path.join(root, d), target)
                    items.append({"name": rel, "type": "papka"})
                for f in files:
                    rel = os.path.relpath(os.path.join(root, f), target)
                    size = os.path.getsize(os.path.join(root, f))
                    items.append({"name": rel, "type": "fayl", "size": f"{size}b"})
        else:
            for entry in os.scandir(target):
                if entry.is_dir():
                    items.append({"name": entry.name, "type": "📁 papka"})
                else:
                    items.append({"name": entry.name, "type": "📄 fayl", "size": f"{entry.stat().st_size}b"})

        return {
            "success": True,
            "path": target,
            "count": len(items),
            "items": items
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_folder(path: str) -> dict:
    """Yangi papka yaratadi"""
    try:
        full_path = _safe_path(path)
        os.makedirs(full_path, exist_ok=True)
        return {"success": True, "message": f"✅ Papka yaratildi: {path}", "path": full_path}
    except Exception as e:
        return {"success": False, "error": str(e)}


def copy_file(source: str, destination: str) -> dict:
    """Faylni nusxa oladi"""
    try:
        src = _safe_path(source)
        dst = _safe_path(destination)
        if not os.path.exists(src):
            return {"success": False, "error": f"Manba topilmadi: {source}"}
        os.makedirs(os.path.dirname(dst) if os.path.dirname(dst) else ".", exist_ok=True)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return {"success": True, "message": f"✅ Nusxa olindi: {source} → {destination}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def move_file(source: str, destination: str) -> dict:
    """Faylni ko'chiradi yoki nomini o'zgartiradi"""
    try:
        src = _safe_path(source)
        dst = _safe_path(destination)
        if not os.path.exists(src):
            return {"success": False, "error": f"Manba topilmadi: {source}"}
        os.makedirs(os.path.dirname(dst) if os.path.dirname(dst) else ".", exist_ok=True)
        shutil.move(src, dst)
        return {"success": True, "message": f"✅ Ko'chirildi: {source} → {destination}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_in_files(query: str, path: str = None) -> dict:
    """Fayllar ichida matn qidiradi"""
    try:
        target = _safe_path(path) if path else WORKSPACE
        results = []
        for root, dirs, files in os.walk(target):
            # Yashirin papkalarni o'tkazib yuborish
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                    for i, line in enumerate(lines, 1):
                        if query.lower() in line.lower():
                            results.append({
                                "file": os.path.relpath(fpath, target),
                                "line": i,
                                "text": line.strip()
                            })
                except Exception:
                    continue
        return {
            "success": True,
            "query": query,
            "found": len(results),
            "results": results[:50]  # maksimum 50 ta
        }
    except Exception as e:
        return {"success": False, "error": str(e)}



def list_files_by_date(when: str = "today", folder: str = None, extension: str = None) -> dict:
    """
    Sana bo'yicha fayllarni topadi (o'zgartirilgan vaqti bo'yicha).
    when: 'today' (bugun), 'yesterday' (kecha), 'week' (oxirgi 7 kun)
    folder: qidirish papkasi (bo'sh bo'lsa - butun foydalanuvchi papkasi)
    extension: faqat shu kengaytma (masalan '.pdf', '.jpg')
    """
    import time
    from datetime import datetime, timedelta

    try:
        now = datetime.now()
        if when == "yesterday":
            start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif when == "week":
            start = now - timedelta(days=7)
            end = now + timedelta(days=1)
        else:  # today
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now + timedelta(days=1)

        start_ts, end_ts = start.timestamp(), end.timestamp()

        # Qidirish papkasi - ko'rsatilmasa, foydalanuvchi asosiy papkalari
        if folder:
            search_dirs = [_safe_path(folder)]
        else:
            home = os.path.expanduser("~")
            search_dirs = [
                os.path.join(home, "Desktop"),
                os.path.join(home, "Downloads"),
                os.path.join(home, "Documents"),
                os.path.join(home, "Pictures"),
                WORKSPACE,
            ]

        results = []
        for d in search_dirs:
            if not os.path.isdir(d):
                continue
            for root, dirs, files in os.walk(d):
                dirs[:] = [x for x in dirs if not x.startswith('.')]
                # Juda chuqur ketmaslik uchun
                if root[len(d):].count(os.sep) > 3:
                    dirs[:] = []
                    continue
                for fname in files:
                    if extension and not fname.lower().endswith(extension.lower()):
                        continue
                    fpath = os.path.join(root, fname)
                    try:
                        mtime = os.path.getmtime(fpath)
                        if start_ts <= mtime < end_ts:
                            results.append({
                                "name": fname,
                                "folder": root,
                                "size": f"{os.path.getsize(fpath)//1024} KB",
                                "time": datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M"),
                            })
                    except OSError:
                        continue
            if len(results) > 200:
                break

        results.sort(key=lambda x: x["time"], reverse=True)
        label = {"today": "bugun", "yesterday": "kecha", "week": "oxirgi hafta"}.get(when, when)
        return {
            "success": True,
            "period": label,
            "found": len(results),
            "files": results[:80],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
