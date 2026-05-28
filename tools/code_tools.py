"""
Kod yozish, tahlil qilish va ishga tushirish toollari
"""

import subprocess
import os
import tempfile
import sys


WORKSPACE = os.getenv("WORKSPACE_DIR", "./workspace")


def run_python_code(code: str) -> dict:
    """Python kodni xavfsiz muhitda bajaradi"""
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=WORKSPACE
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout[:3000] if result.stdout else "",
                "error": result.stderr[:1000] if result.stderr else "",
                "return_code": result.returncode
            }
        finally:
            os.unlink(tmp_path)

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Kod 30 soniyada tugamadi"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def analyze_code(code: str, language: str = "python") -> dict:
    """Kodni tahlil qiladi"""
    try:
        issues = []
        suggestions = []
        lines = code.split('\n')

        if language.lower() == "python":
            for i, line in enumerate(lines, 1):
                stripped = line.strip()

                # Xatolarni tekshirish
                if 'except:' in line and 'except Exception' not in line:
                    issues.append(f"Satr {i}: Umumiy except ishlatilgan - aniq exception turi yozing")

                if 'print(' in line and i > 5:
                    suggestions.append(f"Satr {i}: print() o'rniga logging ishlatishni o'ylab ko'ring")

                if len(line) > 100:
                    suggestions.append(f"Satr {i}: Satr juda uzun ({len(line)} belgi) - 79 ta belgi tavsiya qilinadi")

                if stripped.startswith('import *'):
                    issues.append(f"Satr {i}: 'import *' ishlatish yaxshi emas")

        return {
            "success": True,
            "language": language,
            "total_lines": len(lines),
            "issues_found": len(issues),
            "issues": issues,
            "suggestions": suggestions,
            "summary": f"{len(issues)} muammo, {len(suggestions)} tavsiya topildi"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def generate_code(task: str, language: str = "python", save_path: str = None) -> dict:
    """Vazifa uchun kod yozadi (agent o'zi hal qiladi)"""
    # Bu funksiya agent tomonidan chaqiriladi
    # Asosiy kod generatsiyasi Gemini tomonidan amalga oshiriladi
    # Bu yerda faqat natijani saqlash logikasi bor

    if save_path:
        full_path = os.path.join(WORKSPACE, save_path) if not os.path.isabs(save_path) else save_path
        return {
            "success": True,
            "message": f"Kod {save_path} ga saqlanish uchun tayyor",
            "task": task,
            "language": language,
            "save_path": full_path
        }

    return {
        "success": True,
        "message": "Kod generatsiya qilinmoqda",
        "task": task,
        "language": language
    }
