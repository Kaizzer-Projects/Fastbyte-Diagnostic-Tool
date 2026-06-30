import sys
import psutil
import cpuinfo
import subprocess
from PyQt5 import QtWidgets, QtCore, QtGui

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FastByte Diagnostic Tool")
        self.setFixedSize(1280, 720)

        info = cpuinfo.get_cpu_info()
        self.cpu_model = info.get("brand_raw", "N/A")
        self.cpu_vendor = info.get("vendor_id_raw", "N/A")
        self.cpu_cores = psutil.cpu_count(logical=False)
        self.cpu_threads = psutil.cpu_count(logical=True)

        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QLabel { color: #E0E0E0; font-family: 'Inter'; font-size: 14px; }
            QPushButton {
                background-color: #3A6EA5; color: white; border-radius: 6px;
                padding: 6px 12px; font-family: 'Inter'; font-weight: bold;
            }
            QPushButton:hover { background-color: #558CC9; }
            QFrame { background-color: #1E1E1E; border-radius: 8px; padding: 10px; }
        """)

        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Cabeçalho
        header_frame = QtWidgets.QFrame()
        header_layout = QtWidgets.QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)
        header_layout.setSpacing(10)

        logo = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap("src/fastbyte/resources/fastbyte.png")
        pixmap = pixmap.scaled(60, 60, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        logo.setPixmap(pixmap)

        header = QtWidgets.QLabel("FastByte - Diagnóstico do Sistema")
        header.setStyleSheet("font-size: 20px; font-weight: bold; color: #FFFFFF;")

        header_layout.addWidget(logo, alignment=QtCore.Qt.AlignLeft)
        header_layout.addWidget(header, alignment=QtCore.Qt.AlignLeft)
        header_layout.addStretch()
        main_layout.addWidget(header_frame)

        # Diagnóstico rápido
        self.diagnosis_label = QtWidgets.QLabel()
        self.diagnosis_label.setStyleSheet("font-size: 14px; color: #FFD700;")
        main_layout.addWidget(self.diagnosis_label)

        grid = QtWidgets.QGridLayout()
        main_layout.addLayout(grid)

        # CPU card
        self.cpu_summary = QtWidgets.QLabel()
        self.cpu_button = QtWidgets.QPushButton("Ver detalhes da CPU")
        self.cpu_button.clicked.connect(self.toggle_cpu_details)
        self.cpu_details = QtWidgets.QLabel()
        self.cpu_details.setVisible(False)
        cpu_card = self.create_card("🖥️ CPU", self.cpu_summary, self.cpu_button, self.cpu_details)
        grid.addWidget(cpu_card, 0, 0)

        # RAM card
        self.ram_summary = QtWidgets.QLabel()
        self.ram_button = QtWidgets.QPushButton("Ver detalhes da RAM")
        self.ram_button.clicked.connect(self.toggle_ram_details)
        self.ram_details = QtWidgets.QLabel()
        self.ram_details.setVisible(False)
        ram_card = self.create_card("💾 RAM", self.ram_summary, self.ram_button, self.ram_details)
        grid.addWidget(ram_card, 0, 1)

        # Disco card
        self.disk_label = QtWidgets.QLabel()
        disk_card = self.create_card("📂 Disco", self.disk_label)
        grid.addWidget(disk_card, 0, 2)

        # Botões
        btn_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(btn_layout)
        btn_refresh = QtWidgets.QPushButton("Atualizar")
        btn_report = QtWidgets.QPushButton("Gerar Relatório")
        btn_settings = QtWidgets.QPushButton("Configurações")
        btn_refresh.clicked.connect(self.update_stats)
        btn_report.clicked.connect(self.generate_report)
        btn_settings.clicked.connect(self.open_settings)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addWidget(btn_report)
        btn_layout.addWidget(btn_settings)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)
        self.update_stats()

    def create_card(self, title, content_label, button=None, details=None):
        frame = QtWidgets.QFrame()
        layout = QtWidgets.QVBoxLayout(frame)
        lbl_title = QtWidgets.QLabel(title)
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #FFFFFF;")
        content_label.setStyleSheet("font-size: 14px; color: #E0E0E0;")
        layout.addWidget(lbl_title)
        layout.addWidget(content_label)
        if button:
            layout.addWidget(button)
        if details:
            layout.addWidget(details)
        return frame

    def get_ram_info_linux(self):
        try:
            output = subprocess.check_output(["dmidecode", "-t", "memory"], text=True)
            slots_used = output.count("Size:")
            freq_lines = [line for line in output.splitlines() if "Speed:" in line and "Configured" not in line]
            freq = freq_lines[0].split(":")[1].strip() if freq_lines else "N/A"
            if "ChannelA" in output and "ChannelB" in output:
                channel = "Dual-channel"
            elif "ChannelA" in output:
                channel = "Single-channel"
            else:
                channel = "Informação não disponível"
            return slots_used, freq, channel
        except Exception:
            return "N/A", "N/A", "N/A"

    def update_stats(self):
        freq = psutil.cpu_freq()
        cpu_clock = f"{freq.current:.2f} MHz" if freq else "N/A"
        self.cpu_summary.setText(f"Modelo: {self.cpu_model}\nClock Atual: {cpu_clock}")

        ram = psutil.virtual_memory()
        total_ram_gb = round(ram.total / (1024**3), 2)
        used_ram_gb = round(ram.used / (1024**3), 2)
        self.ram_summary.setText(f"Total instalado: {total_ram_gb} GB\nUso atual: {used_ram_gb} GB ({ram.percent}%)")

        disk = psutil.disk_usage('/')
        self.disk_label.setText(f"Uso atual: {disk.percent}%")

        diagnosis = []
        if ram.percent > 85:
            diagnosis.append(f"⚠️ RAM em {ram.percent}%, risco de falta de memória.")
        if disk.percent > 90:
            diagnosis.append(f"⚠️ Disco em {disk.percent}%, pouco espaço disponível.")
        if freq and freq.current > freq.max * 0.95:
            diagnosis.append("⚠️ CPU operando próximo ao limite de clock.")
        if not diagnosis:
            diagnosis.append("✅ Sistema em condições normais.")
        self.diagnosis_label.setText("\n".join(diagnosis))

        if self.cpu_details.isVisible():
            self.cpu_details.setText(
                f"Modelo: {self.cpu_model}\n"
                f"Fabricante: {self.cpu_vendor}\n"
                f"Núcleos: {self.cpu_cores}\n"
                f"Threads: {self.cpu_threads}\n"
                f"Clock Base: {freq.max:.2f} MHz\n"
                f"Clock Atual: {cpu_clock}"
            )

        if self.ram_details.isVisible():
            slots, freq_ram, channel = self.get_ram_info_linux()
            self.ram_details.setText(
                f"Total instalado: {total_ram_gb} GB\n"
                f"Uso atual: {used_ram_gb} GB ({ram.percent}%)\n"
                f"Frequência atual: {freq_ram}\n"
                f"Slots usados: {slots}\n"
                f"Channel: {channel}"
            )

    def toggle_cpu_details(self):
        self.cpu_details.setVisible(not self.cpu_details.isVisible())
        self.update_stats()

    def toggle_ram_details(self):
        self.ram_details.setVisible(not self.ram_details.isVisible())
        self.update_stats()

    def generate_report(self):
        QtWidgets.QMessageBox.information(self, "Relatório", "Função de relatório em desenvolvimento.")

    def open_settings(self):
        QtWidgets.QMessageBox.information(self, "Configurações", "Tela de configurações em desenvolvimento.")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
