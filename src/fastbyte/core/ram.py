import psutil
import subprocess


def get_ram_basic():
    ram = psutil.virtual_memory()

    return {
        "total_gb": round(ram.total / (1024**3), 2),
        "used_gb": round(ram.used / (1024**3), 2),
        "percent": ram.percent
    }


def get_ram_advanced_linux():
    try:
        output = subprocess.check_output(["dmidecode", "-t", "memory"], text=True, stderr=subprocess.DEVNULL)

        slots = output.count("Size:")

        freq = "N/A"
        for line in output.splitlines():
            if "Speed:" in line and "Configured" not in line:
                freq = line.split(":")[1].strip()
                break

        channel = "Informação não disponível (requer permissão root)"

        return {
            "slots_used": slots,
            "frequency": freq,
            "channel": channel,
            "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
            "percent": psutil.virtual_memory().percent
        }

    except Exception:
        return {
            "slots_used": "N/A (sem permissão)",
            "frequency": "N/A (sem permissão)",
            "channel": "Limitado por permissões do sistema",
            "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
            "percent": psutil.virtual_memory().percent
        }
