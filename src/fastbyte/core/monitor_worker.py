import psutil
import time
import platform
from PySide6.QtCore import QThread, Signal


class MonitorWorker(QThread):
    data = Signal(dict)

    def __init__(self):
        super().__init__()

        psutil.cpu_percent(interval=None)
        for p in psutil.process_iter():
            try:
                p.cpu_percent(None)
            except:
                pass

    def run(self):

        while not self.isInterruptionRequested():

            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            try:
                cpu_mhz = psutil.cpu_freq().current
            except:
                cpu_mhz = 0

            cpu_name = self.get_cpu_name()

            procs = []
            for p in psutil.process_iter(['pid', 'name']):
                try:
                    procs.append({
                        "pid": p.pid,
                        "name": p.info['name'],
                        "cpu_percent": p.cpu_percent(interval=None),
                        "memory_percent": p.memory_percent()
                    })
                except:
                    continue

            top_procs = sorted(
                procs,
                key=lambda x: x["cpu_percent"],
                reverse=True
            )[:5]

            diagnosis = self.generate_diagnosis(cpu, ram, disk)

            data = {
                "cpu": cpu,
                "cpu_mhz": cpu_mhz,
                "cpu_name": cpu_name,

                "ram": ram.percent,
                "ram_used_gb": ram.used / (1024**3),
                "ram_total_gb": ram.total / (1024**3),
                "ram_freq": self.get_ram_freq(),
                "ram_slots": self.safe_ram_slots(),

                "disk": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
                "disk_total_gb": disk.total / (1024**3),

                "top_processes": top_procs,
                "diagnosis": diagnosis
            }

            self.data.emit(data)
            time.sleep(1)

        self.quit()
        return

    def generate_diagnosis(self, cpu, ram, disk):

        issues = []

        if cpu > 85:
            issues.append("🔴 CPU sobrecarregada")

        if ram.percent > 85:
            issues.append("🔴 RAM em nível crítico")

        if disk.percent > 90:
            issues.append("🔴 Disco quase cheio")

        if cpu > 60 and ram.percent > 70:
            issues.append("🟡 Multitarefa pesada detectada")

        if not issues:
            return "🟢 Sistema fluido e sem gargalos"

        return " | ".join(issues)

    def get_cpu_name(self):
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
        except:
            pass

        return platform.processor() or "CPU desconhecido"

    def get_ram_freq(self):
        try:
            import subprocess
            out = subprocess.getoutput("dmidecode 2>/dev/null | grep -i speed | head -n 1")
            return out.split(":")[-1].strip() if ":" in out else "N/A"
        except:
            return "N/A"

    def safe_ram_slots(self):
        try:
            import subprocess
            out = subprocess.getoutput("lsblk -o NAME,TYPE | grep disk")
            return len(out.splitlines()) if out else 0
        except:
            return 0
