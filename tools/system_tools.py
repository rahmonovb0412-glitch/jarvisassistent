"""
Sistema boshqarish toollari - buyruqlar, jarayonlar, paketlar
"""

import subprocess
import psutil
import platform
import os


def get_system_info() -> dict:
    """Kompyuter haqida to'liq ma'lumot"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            "success": True,
            "os": f"{platform.system()} {platform.release()}",
            "processor": platform.processor() or platform.machine(),
            "cpu_cores": psutil.cpu_count(),
            "cpu_usage": f"{cpu_percent}%",
            "ram_total": f"{ram.total // (1024**3)} GB",
            "ram_used": f"{ram.used // (1024**3)} GB ({ram.percent}%)",
            "ram_free": f"{ram.available // (1024**3)} GB",
            "disk_total": f"{disk.total // (1024**3)} GB",
            "disk_used": f"{disk.used // (1024**3)} GB ({disk.percent}%)",
            "disk_free": f"{disk.free // (1024**3)} GB",
            "python_version": platform.python_version(),
            "hostname": platform.node()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_command(command: str, timeout: int = 30) -> dict:
    """Terminal buyrug'ini bajaradi"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.getenv("WORKSPACE_DIR", "./workspace")
        )
        return {
            "success": result.returncode == 0,
            "command": command,
            "stdout": result.stdout[:3000] if result.stdout else "",
            "stderr": result.stderr[:1000] if result.stderr else "",
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Buyruq {timeout} soniyada tugamadi (timeout)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def install_package(package: str, manager: str = "pip") -> dict:
    """Paket o'rnatadi"""
    try:
        if manager == "npm":
            cmd = f"npm install -g {package}"
        else:
            cmd = f"pip install {package}"

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            return {
                "success": True,
                "message": f"✅ {package} muvaffaqiyatli o'rnatildi",
                "output": result.stdout[-500:] if result.stdout else ""
            }
        else:
            return {
                "success": False,
                "error": result.stderr[-500:] if result.stderr else "Noma'lum xato"
            }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "O'rnatish juda uzoq vaqt oldi"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_processes() -> dict:
    """Ishlab turgan jarayonlarni ro'yxatlaydi"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = proc.info
                if info['cpu_percent'] > 0 or info['memory_percent'] > 0.1:
                    processes.append({
                        "pid": info['pid'],
                        "name": info['name'],
                        "cpu": f"{info['cpu_percent']:.1f}%",
                        "ram": f"{info['memory_percent']:.1f}%",
                        "status": info['status']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda x: float(x['cpu'].replace('%', '')), reverse=True)

        return {
            "success": True,
            "total": len(processes),
            "top_processes": processes[:20]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def kill_process(pid: int) -> dict:
    """Jarayonni to'xtatadi"""
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        return {"success": True, "message": f"✅ Jarayon {pid} to'xtatildi"}
    except psutil.NoSuchProcess:
        return {"success": False, "error": f"Jarayon {pid} topilmadi"}
    except Exception as e:
        return {"success": False, "error": str(e)}



def clean_junk_files(dry_run: bool = True) -> dict:
    """
    Keraksiz vaqtinchalik (temp/cache) fayllarni tozalaydi.
    XAVFSIZ: faqat tizimning temp papkalarini tegadi, shaxsiy fayllarga tegmaydi.
    dry_run=True bo'lsa - faqat hisoblaydi, o'chirmaydi (avval ko'rsatadi).
    dry_run=False bo'lsa - haqiqatan o'chiradi.
    """
    import tempfile
    import glob as _glob

    try:
        targets = []
        system = platform.system()
        home = os.path.expanduser("~")

        # Xavfsiz temp papkalar
        targets.append(tempfile.gettempdir())
        if system == "Windows":
            targets += [
                os.path.join(home, "AppData", "Local", "Temp"),
                os.environ.get("TEMP", ""),
                os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Temp"),
            ]
        else:
            targets += ["/tmp", os.path.join(home, ".cache")]

        targets = [t for t in targets if t and os.path.isdir(t)]
        targets = list(dict.fromkeys(targets))  # dublikatlarni olib tashlash

        total_size = 0
        total_count = 0
        deleted = 0
        errors = 0
        cutoff = None  # hammasi

        for tdir in targets:
            for entry in _glob.glob(os.path.join(tdir, "*")):
                try:
                    if os.path.isfile(entry):
                        sz = os.path.getsize(entry)
                    elif os.path.isdir(entry):
                        sz = sum(
                            os.path.getsize(os.path.join(r, f))
                            for r, _, fs in os.walk(entry) for f in fs
                            if os.path.exists(os.path.join(r, f))
                        )
                    else:
                        continue
                    total_size += sz
                    total_count += 1

                    if not dry_run:
                        try:
                            if os.path.isfile(entry):
                                os.remove(entry)
                            else:
                                import shutil as _sh
                                _sh.rmtree(entry, ignore_errors=True)
                            deleted += 1
                        except (PermissionError, OSError):
                            errors += 1  # ishlatilayotgan fayllar
                except (OSError, PermissionError):
                    errors += 1
                    continue

        mb = total_size / (1024 * 1024)
        if dry_run:
            return {
                "success": True,
                "mode": "tekshiruv (o'chirilmadi)",
                "papkalar": targets,
                "topilgan_fayllar": total_count,
                "bo'shatish_mumkin": f"{mb:.1f} MB",
                "izoh": f"{mb:.1f} MB keraksiz fayl topildi. O'chirish uchun dry_run=False bilan qayta chaqiring.",
            }
        return {
            "success": True,
            "mode": "tozalandi",
            "o'chirilgan": deleted,
            "bo'shatildi": f"{mb:.1f} MB",
            "o'tkazib_yuborilgan": errors,
            "izoh": f"✅ {deleted} ta element o'chirildi, ~{mb:.1f} MB bo'shatildi. ({errors} ta band fayl o'tkazib yuborildi)",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
