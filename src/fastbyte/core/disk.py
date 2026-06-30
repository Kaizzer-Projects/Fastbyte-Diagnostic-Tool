import psutil


def get_disk_info(path="/"):
    disk = psutil.disk_usage(path)

    return {
        "total_gb": round(disk.total / (1024**3), 2),
        "used_gb": round(disk.used / (1024**3), 2),
        "percent": disk.percent
    }
