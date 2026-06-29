from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QProgressBar, QStackedLayout,
    QFileDialog
)

from PySide6.QtGui import QFont

from .core.monitor_worker import MonitorWorker
from .core.reports import generate_pdf_report


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("FastByte Diagnóstico de PC")
        self.resize(1200, 700)

        central = QWidget()
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)

        # ================= MENU =================
        menu = QVBoxLayout()
        menu.setContentsMargins(15, 15, 15, 15)
        menu.setSpacing(10)

        self.logo = QLabel("FastByte")
        self.logo.setFont(QFont("Arial", 20, QFont.Bold))
        self.logo.setAlignment(Qt.AlignCenter)
        self.logo.setStyleSheet("color:#00d4ff; padding:10px;")

        self.btn_sys = QPushButton("🖥 Sistema")
        self.btn_cpu = QPushButton("🧠 CPU")
        self.btn_ram = QPushButton("🧩 RAM")
        self.btn_disk = QPushButton("💾 Disco")
        self.btn_report = QPushButton("📄 Relatório")

        for b in [self.btn_sys, self.btn_cpu, self.btn_ram, self.btn_disk, self.btn_report]:
            b.setMinimumHeight(40)

        menu.addWidget(self.logo)
        menu.addWidget(self.btn_sys)
        menu.addWidget(self.btn_cpu)
        menu.addWidget(self.btn_ram)
        menu.addWidget(self.btn_disk)
        menu.addWidget(self.btn_report)
        menu.addStretch()

        # ================= STACK =================
        self.stack = QStackedLayout()

        self.page_sys = QWidget()
        self.page_cpu = QWidget()
        self.page_ram = QWidget()
        self.page_disk = QWidget()

        self.stack.addWidget(self.page_sys)
        self.stack.addWidget(self.page_cpu)
        self.stack.addWidget(self.page_ram)
        self.stack.addWidget(self.page_disk)

        container = QWidget()
        container.setLayout(self.stack)

        root.addLayout(menu, 1)
        root.addWidget(container, 4)

        self.btn_sys.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_sys))
        self.btn_cpu.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_cpu))
        self.btn_ram.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_ram))
        self.btn_disk.clicked.connect(lambda: self.stack.setCurrentWidget(self.page_disk))

        self.btn_report.clicked.connect(self.generate_report)

        self.worker = MonitorWorker()
        self.worker.data.connect(self.update)
        self.worker.start()

        self.build_ui()

    # ================= PADRÃO DE PÁGINA (OFFSET VISUAL) =================
    def page_layout(self, widget):
        layout = QVBoxLayout(widget)

        # 🔥 AQUI É O AJUSTE QUE VOCÊ PEDIU
        layout.setContentsMargins(20, 25, 20, 20)  # topo maior = +2 linhas visuais
        layout.setSpacing(12)

        return layout

    # ================= STATUS =================
    def cpu_msg(self, v):
        if v < 30:
            return "🟢 Sistema fluido (uso baixo)"
        elif v <= 60:
            return "🟡 Uso moderado"
        return "🔴 Uso alto"

    def ram_msg(self, v):
        if v < 35:
            return "🟢 RAM ok"
        elif v <= 70:
            return "🟡 RAM moderada"
        return "🔴 RAM crítica"

    def disk_msg(self, v):
        if v < 70:
            return "🟢 Disco saudável"
        elif v < 85:
            return "🟡 Atenção no disco"
        return "🔴 Disco crítico"

    # ================= UI =================
    def build_ui(self):

        # ================= SISTEMA =================
        sys = self.page_layout(self.page_sys)

        self.sys_cpu_model = QLabel()
        self.sys_cpu_status = QLabel()
        self.sys_cpu_bar = QProgressBar()

        self.sys_ram_info = QLabel()
        self.sys_ram_status = QLabel()
        self.sys_ram_bar = QProgressBar()

        self.sys_disk_info = QLabel()
        self.sys_disk_status = QLabel()
        self.sys_disk_bar = QProgressBar()

        sys.addWidget(self.sys_cpu_model)
        sys.addWidget(self.sys_cpu_status)
        sys.addWidget(self.sys_cpu_bar)

        sys.addWidget(self.sys_ram_info)
        sys.addWidget(self.sys_ram_status)
        sys.addWidget(self.sys_ram_bar)

        sys.addWidget(self.sys_disk_info)
        sys.addWidget(self.sys_disk_status)
        sys.addWidget(self.sys_disk_bar)

        sys.addStretch()

        # ================= CPU =================
        cpu = self.page_layout(self.page_cpu)

        self.cpu_model = QLabel()
        self.cpu_status = QLabel()
        self.cpu_clock = QLabel()
        self.cpu_bar = QProgressBar()

        cpu.addWidget(self.cpu_model)
        cpu.addWidget(self.cpu_status)
        cpu.addWidget(self.cpu_clock)
        cpu.addWidget(self.cpu_bar)
        cpu.addStretch()

        # ================= RAM =================
        ram = self.page_layout(self.page_ram)

        self.ram_status = QLabel()
        self.ram_detail = QLabel()
        self.ram_extra = QLabel()
        self.ram_bar = QProgressBar()

        ram.addWidget(self.ram_status)
        ram.addWidget(self.ram_detail)
        ram.addWidget(self.ram_extra)
        ram.addWidget(self.ram_bar)
        ram.addStretch()

        # ================= DISCO =================
        disk = self.page_layout(self.page_disk)

        self.disk_status = QLabel()
        self.disk_detail = QLabel()
        self.disk_health = QLabel()
        self.disk_bar = QProgressBar()

        disk.addWidget(self.disk_status)
        disk.addWidget(self.disk_detail)
        disk.addWidget(self.disk_health)
        disk.addWidget(self.disk_bar)
        disk.addStretch()

    # ================= UPDATE =================
    def update(self, d):

        if not d:
            return

        # SISTEMA
        self.sys_cpu_model.setText(f"CPU: {d.get('cpu_name','')}")
        self.sys_cpu_status.setText(self.cpu_msg(d.get("cpu", 0)))
        self.sys_cpu_bar.setValue(d.get("cpu", 0))

        self.sys_ram_info.setText(f"RAM: {d.get('ram_total_gb',0):.2f} GB")
        self.sys_ram_status.setText(self.ram_msg(d.get("ram", 0)))
        self.sys_ram_bar.setValue(d.get("ram", 0))

        self.sys_disk_info.setText(f"DISCO: {d.get('disk_total_gb',0):.2f} GB")
        self.sys_disk_status.setText(self.disk_msg(d.get("disk", 0)))
        self.sys_disk_bar.setValue(d.get("disk", 0))

        # CPU
        self.cpu_model.setText(f"Modelo: {d.get('cpu_name','')}")
        self.cpu_status.setText(self.cpu_msg(d.get("cpu", 0)))
        self.cpu_clock.setText(f"Velocidade: {d.get('cpu_mhz',0):.0f} MHz")
        self.cpu_bar.setValue(d.get("cpu", 0))

        # RAM
        self.ram_status.setText(self.ram_msg(d.get("ram", 0)))
        self.ram_detail.setText(f"{d.get('ram_used_gb',0):.2f}/{d.get('ram_total_gb',0):.2f} GB")
        self.ram_extra.setText(f"Freq: {d.get('ram_freq')} | Slots: {d.get('ram_slots')}")
        self.ram_bar.setValue(d.get("ram", 0))

        # DISCO
        self.disk_status.setText(self.disk_msg(d.get("disk", 0)))
        self.disk_detail.setText(f"Uso: {d.get('disk',0):.1f}% | Livre: {d.get('disk_free_gb',0):.2f} GB")
        self.disk_health.setText(d.get("disk_health",""))
        self.disk_bar.setValue(d.get("disk", 0))

    def generate_report(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar relatório", "relatorio_fastbyte.pdf", "PDF (*.pdf)"
        )
        if path:
            if not path.endswith(".pdf"):
                path += ".pdf"
            generate_pdf_report(path)
