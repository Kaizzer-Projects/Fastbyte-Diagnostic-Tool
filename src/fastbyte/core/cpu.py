import psutil
import cpuinfo
import time


_last_read = None


def _smooth(value):
    global _last_read
    if value is None:
        return 0
    if _last_read is None:
        _last_read = value
        return value
    # suavização para evitar 0.0GHz e jitter
    value = (_last_read * 0.6) + (value * 0.4)
    _last_read = value
    return value


def get_cpu_info():
    info = cpuinfo.get_cpu_info()
    freq = psutil.cpu_freq(percpu=True)

    if freq:
        current = sum(f.current for f in freq if f.current) / len(freq)
        base = sum(f.max for f in freq if f.max) / len(freq)
    else:
        current = 0
        base = 0

    current = _smooth(current)
    base = _smooth(base)

    return {
        "model": info.get("brand_raw", "N/A"),
        "vendor": info.get("vendor_id_raw", "N/A"),
        "cores": psutil.cpu_count(logical=False),
        "threads": psutil.cpu_count(logical=True),

        "base_clock": base,
        "current_clock": current
    }
