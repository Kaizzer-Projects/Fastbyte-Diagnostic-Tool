import re
import subprocess
import time

_cache = {"time": 0, "data": None}


def _run(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except:
        return ""


def get_gpu():
    global _cache

    now = time.time()

    # CACHE (evita travar UI)
    if _cache["data"] and now - _cache["time"] < 1:
        return _cache["data"]

    vendor, name = "Desconhecido", "GPU não encontrada"

    for line in _run(["lspci"]).splitlines():
        if "VGA" in line or "3D controller" in line:
            name = line.split(":")[-1].strip()
            u = line.upper()
            if "AMD" in u:
                vendor = "AMD"
            elif "NVIDIA" in u:
                vendor = "NVIDIA"
            elif "INTEL" in u:
                vendor = "Intel"
            break

    output = _run(["radeontop", "-d", "-", "-l", "1"])
    line = output.splitlines()[-1] if output else ""

    def f(pattern):
        m = re.search(pattern, line)
        return float(m.group(1)) if m else None

    data = {
        "name": name,
        "vendor": vendor,
        "usage": f(r"gpu ([0-9.]+)%") or 0,
        "vram_percent": f(r"vram ([0-9.]+)%"),
        "vram_used_mb": f(r"vram [0-9.]+% ([0-9.]+)mb"),
        "gtt_percent": f(r"gtt ([0-9.]+)%"),
        "gtt_used_mb": f(r"gtt [0-9.]+% ([0-9.]+)mb"),
        "core_clock": None,
        "memory_clock": None
    }

    _cache = {"time": now, "data": data}
    return data
