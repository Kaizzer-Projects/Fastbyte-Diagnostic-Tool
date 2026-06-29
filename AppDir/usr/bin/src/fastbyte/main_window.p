from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QProgressBar, QFrame
)

from .core.system import get_cpu, get_ram, get_disk


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Fastbyte Diagnóstico de PC")
        self.resize(1200, 700)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QHBoxLayout(central)

        # ===== MENU =====
        sidebar = QVBoxLayout()

        title = QLabel("Fastbyte Diagnóstico de PC")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.btn_sys = QPushButton("Sistema")
        self.btn_cpu = QPushButton("CPU")
        self.btn_ram = QPushButton("RAM")
        self.btn_disk = QPushButton("Disco")

        for b in [self.btn_sys, self.btn_cpu, self.btn_ram, self.btn_disk]:
            b.setMinimumHeight(40)

        sidebar.addWidget(title)
        sidebar.addWidget(self.btn_sys)
        sidebar.addWidget(self.btn_cpu)
        sidebar.addWidget(self.btn_ram)
        sidebar.addWidget(self.btn_disk)
        sidebar.addStretch()

        # ===== ÁREA =====
        self.content = QVBoxLayout()

        container = QWidget()
        container.setLayout(self.content)

        layout.addLayout(sidebar, 1)
        layout.addWidget(container, 4)

        # ===== CARDS =====
        self.cpu = self.create_card("💻 CPU")
        self.ram = self.create_card("🧠 RAM")
        self.disk = self.create_card("💽 DISCO")

        self.content.addWidget(self.cpu["box"])
        self.content.addWidget(self.ram["box"])
        self.content.addWidget(self.disk["box"])

        # ===== TIMER =====
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)

        self.update()

    # ===== CARD PROFISSIONAL =====
    def create_card(self, name):
        box = QFrame()
        box.setStyleSheet("padding: 12px; border-radius: 8px;")

        layout = QVBoxLayout(box)

        title = QLabel(name)
        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        bar = QProgressBar()
        bar.setTextVisible(True)

        status = QLabel("--")
        status.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(bar)
        layout.addWidget(status)

        return {"box": box, "bar": bar, "status": status}

    # ===== ESTILO DE STATUS =====
    def format_cpu(self, v):
        if v < 40:
            return "🟢 CPU OK — sistema fluido"
        elif v < 65:
            return "🟡 CPU moderada — uso equilibrado"
        elif v < 85:
            return "🟠 CPU alta — atenção"
        return "🔴 CPU crítica — sobrecarga"

    def format_ram(self, v):
        if v < 40:
            return "🟢 RAM OK — uso baixo"
        elif v < 65:
            return "🟡 RAM moderada"
        elif v < 85:
            return "🟠 RAM alta — muitos apps abertos"
        return "🔴 RAM crítica — quase cheia"

    def format_disk(self, v):
        free = 100 - v
        if v < 60:
            return f"🟢 Disco OK — {free:.0f}% livre"
        elif v < 75:
            return f"🟡 Disco atenção — {free:.0f}% livre"
        elif v < 90:
            return f"🟠 Disco baixo — pouco espaço"
        return f"🔴 Disco crítico — quase sem espaço"

    # ===== UPDATE =====
    def update(self):
        cpu = get_cpu()
        ram = get_ram()["percent"]
        disk = get_disk()[0]["percent"]

        self.cpu["bar"].setValue(int(cpu))
        self.ram["bar"].setValue(int(ram))
        self.disk["bar"].setValue(int(disk))

        self.cpu["status"].setText(self.format_cpu(cpu))
        self.ram["status"].setText(self.format_ram(ram))
        self.disk["status"].setText(self.format_disk(disk))
