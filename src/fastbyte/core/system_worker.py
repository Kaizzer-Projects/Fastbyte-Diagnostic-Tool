from PyQt5.QtCore import QThread, pyqtSignal
import psutil
import time
from fastbyte.core.cpu import get_cpu_info


class SystemWorker(QThread):
    data_ready = pyqtSignal(dict)

    def run(self):
        while True:

            cpu = get_cpu_info()
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            cpu["percent"] = psutil.cpu_percent(interval=None)

            self.data_ready.emit({
                "cpu": cpu,
                "ram": {
                    "percent": ram.percent,
                    "used_gb": round(ram.used / (1024**3), 2),
                    "total_gb": round(ram.total / (1024**3), 2),
                },
                "disk": {
                    "percent": disk.percent
                }
            })

            time.sleep(1)
