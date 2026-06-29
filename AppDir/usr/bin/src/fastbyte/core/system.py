import psutil


# ===== CPU =====
def get_cpu():
    return psutil.cpu_percent(interval=0.2)


# ===== RAM =====
def get_ram():
    mem = psutil.virtual_memory()
    return {
        "percent": mem.percent,
        "used": mem.used,
        "total": mem.total
    }


# ===== DISCO (FILTRADO - SOMENTE PRINCIPAIS) =====
def get_disk():
    partitions = psutil.disk_partitions(all=False)

    allowed_mounts = ["/", "/home"]  # foco no essencial
    disks = []

    for p in partitions:
        if p.mountpoint not in allowed_mounts:
            continue

        try:
            usage = psutil.disk_usage(p.mountpoint)

            disks.append({
                "device": p.device,
                "mount": p.mountpoint,
                "percent": usage.percent,
                "used": usage.used,
                "free": usage.free,
                "total": usage.total
            })
        except:
            continue

    # fallback: se não tiver /home separado, garante pelo menos /
    if not disks:
        usage = psutil.disk_usage("/")
        disks.append({
            "device": "system",
            "mount": "/",
            "percent": usage.percent,
            "used": usage.used,
            "free": usage.free,
            "total": usage.total
        })

    return disks


# ===== STATUS GLOBAL =====
def get_status(cpu, ram, disk):
    if cpu > 85 or ram > 85 or disk > 90:
        return "CRÍTICO"
    elif cpu > 65 or ram > 65 or disk > 75:
        return "ATENÇÃO"
    else:
        return "NORMAL"
