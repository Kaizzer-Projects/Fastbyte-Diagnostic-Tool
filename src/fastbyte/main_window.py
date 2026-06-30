from PyQt5 import QtWidgets, QtGui, QtCore
from fastbyte.core.system_worker import SystemWorker


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FastByte Diagnostic Tool")
        self.setFixedSize(1280, 720)

        self.cache = {}

        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QLabel { color: #E0E0E0; font-size: 14px; }
            QPushButton {
                background-color: #3A6EA5;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #558CC9; }
            QFrame { background-color: #1E1E1E; border-radius: 8px; padding: 10px; }
        """)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # ================= HEADER =================
        header = QtWidgets.QFrame()
        header_layout = QtWidgets.QHBoxLayout(header)

        logo = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap("fastbyte.png")

        # 🔥 LOGO AUMENTADA
        pixmap = pixmap.scaled(
            80, 80,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        )

        logo.setPixmap(pixmap)

        title = QtWidgets.QLabel("FastByte - Diagnóstico do Sistema")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")

        header_layout.addWidget(logo)
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addWidget(header)

        # ================= DIAGNÓSTICO =================
        self.diagnosis = QtWidgets.QLabel()
        self.diagnosis.setStyleSheet("color: #FFD700;")
        layout.addWidget(self.diagnosis)

        grid = QtWidgets.QGridLayout()
        layout.addLayout(grid)

        # CPU
        self.cpu = QtWidgets.QLabel()
        self.cpu_details = QtWidgets.QLabel()
        self.cpu_details.setVisible(False)
        self.cpu_btn = QtWidgets.QPushButton("Detalhes CPU")
        self.cpu_btn.clicked.connect(self.toggle_cpu)
        grid.addWidget(self.card("🖥️ CPU", self.cpu, self.cpu_btn, self.cpu_details), 0, 0)

        # RAM
        self.ram = QtWidgets.QLabel()
        self.ram_details = QtWidgets.QLabel()
        self.ram_details.setVisible(False)
        self.ram_btn = QtWidgets.QPushButton("Detalhes RAM")
        self.ram_btn.clicked.connect(self.toggle_ram)
        grid.addWidget(self.card("💾 RAM", self.ram, self.ram_btn, self.ram_details), 0, 1)

        # DISCO
        self.disk = QtWidgets.QLabel()
        self.disk_details = QtWidgets.QLabel()
        self.disk_details.setVisible(False)
        self.disk_btn = QtWidgets.QPushButton("Detalhes Disco")
        self.disk_btn.clicked.connect(self.toggle_disk)
        grid.addWidget(self.card("📂 DISCO", self.disk, self.disk_btn, self.disk_details), 0, 2)

        # BOTÕES
        btns = QtWidgets.QHBoxLayout()

        self.btn_update = QtWidgets.QPushButton("Atualizar")
        self.btn_report = QtWidgets.QPushButton("Gerar Relatório")
        self.btn_settings = QtWidgets.QPushButton("Configurações")

        self.btn_update.clicked.connect(self.force_update)
        self.btn_report.clicked.connect(self.report)
        self.btn_settings.clicked.connect(self.settings)

        btns.addWidget(self.btn_update)
        btns.addWidget(self.btn_report)
        btns.addWidget(self.btn_settings)

        layout.addLayout(btns)

        self.worker = SystemWorker()
        self.worker.data_ready.connect(self.update_ui)
        self.worker.start()

    # ================= CARD =================
    def card(self, title, label, btn=None, details=None):
        w = QtWidgets.QFrame()
        l = QtWidgets.QVBoxLayout(w)

        t = QtWidgets.QLabel(title)
        t.setStyleSheet("font-weight: bold; font-size: 16px; color: white;")

        l.addWidget(t)
        l.addWidget(label)

        if btn:
            l.addWidget(btn)
        if details:
            l.addWidget(details)

        return w

    # ================= DISCO =================
    def normalize_disks(self, disk_data):
        if isinstance(disk_data, list):
            return [d for d in disk_data if isinstance(d, dict)]
        if isinstance(disk_data, dict):
            return [disk_data]
        return []

    # ================= UPDATE =================
    def update_ui(self, d):
        self.cache = d

        cpu = d["cpu"]
        ram = d["ram"]
        disk_list = self.normalize_disks(d.get("disk", []))

        cpu_clock = f"{cpu['current_clock']/1000:.2f} GHz"
        base_clock = f"{cpu['base_clock']/1000:.2f} GHz"

        self.cpu.setText(
            f"Modelo: {cpu['model']}\n"
            f"Uso: {cpu['percent']}%\n"
            f"Atual: {cpu_clock}\n"
            f"Base: {base_clock}"
        )

        self.ram.setText(
            f"{ram['percent']}% | {ram['used_gb']}GB/{ram['total_gb']}GB"
        )

        total_disk = max((d.get("percent", 0) for d in disk_list), default=0)
        self.disk.setText(f"{total_disk}%")

        self.diagnose(cpu, ram, disk_list)

        if self.cpu_details.isVisible():
            self.cpu_details.setText(
                f"Modelo: {cpu['model']}\n"
                f"Fabricante: {cpu['vendor']}\n"
                f"Núcleos: {cpu['cores']}\n"
                f"Threads: {cpu['threads']}\n"
                f"Clock Atual: {cpu_clock}\n"
                f"Clock Base: {base_clock}"
            )

        if self.ram_details.isVisible():
            self.ram_details.setText(
                f"Total: {ram['total_gb']} GB\n"
                f"Usado: {ram['used_gb']} GB\n"
                f"Uso: {ram['percent']}%"
            )

        if self.disk_details.isVisible():
            text = ""
            for i, dsk in enumerate(disk_list):
                text += (
                    f"\nDisco {i+1}:\n"
                    f"Uso: {dsk.get('percent',0)}%\n"
                    f"Total: {dsk.get('total_gb',0)} GB\n"
                    f"Usado: {dsk.get('used_gb',0)} GB\n"
                    f"Livre: {dsk.get('free_gb',0)} GB\n"
                    f"Saúde: {self.disk_health(dsk.get('percent',0))}\n"
                )
            self.disk_details.setText(text)

    # ================= DIAGNÓSTICO COMPLETO (RESTORED FULL VERSION) =================
    def diagnose(self, cpu, ram, disk_list):
        msg = []

        cpu_load = cpu["percent"]
        ram_load = ram["percent"]
        disk_load = max((d.get("percent", 0) for d in disk_list), default=0)

        # CPU
        if cpu_load < 30:
            msg.append("🟢 CPU: baixa utilização, sistema altamente responsivo com ampla margem de processamento livre.")
        elif cpu_load < 60:
            msg.append("🟡 CPU: uso moderado, múltiplos processos ativos sem impacto crítico no desempenho.")
        elif cpu_load < 85:
            msg.append("🟠 CPU: carga elevada, possível redução perceptível de performance em tarefas pesadas.")
        else:
            msg.append("🔴 CPU: saturação crítica, risco alto de travamentos e lentidão geral.")

        # RAM
        if ram_load < 50:
            msg.append("🟢 RAM: uso eficiente, grande disponibilidade de memória para multitarefa.")
        elif ram_load < 75:
            msg.append("🟡 RAM: consumo moderado, diversos aplicativos em execução simultânea.")
        elif ram_load < 90:
            msg.append("🟠 RAM: pressão elevada, possível uso de swap e lentidão em multitarefa.")
        else:
            msg.append("🔴 RAM: estado crítico, forte risco de travamentos por falta de memória.")

        # DISCO
        if disk_load < 40:
            msg.append("🟢 DISCO: espaço abundante, operação segura e estável.")
        elif disk_load < 70:
            msg.append("🟡 DISCO: uso crescente, recomenda monitoramento e limpeza futura.")
        elif disk_load < 90:
            msg.append("🟠 DISCO: espaço limitado, ação de limpeza recomendada.")
        else:
            msg.append("🔴 DISCO: crítico, risco de falha operacional por falta de armazenamento.")

        self.diagnosis.setText("\n".join(msg))

    def disk_health(self, p):
        if p < 70:
            return "🟢 Bom"
        elif p < 85:
            return "🟡 Atenção"
        return "🔴 Crítico"

    def toggle_cpu(self):
        self.cpu_details.setVisible(not self.cpu_details.isVisible())

    def toggle_ram(self):
        self.ram_details.setVisible(not self.ram_details.isVisible())

    def toggle_disk(self):
        self.disk_details.setVisible(not self.disk_details.isVisible())

    def force_update(self):
        if self.cache:
            self.update_ui(self.cache)

    def report(self):
        QtWidgets.QMessageBox.information(self, "Relatório", "Em desenvolvimento")

    def settings(self):
        QtWidgets.QMessageBox.information(self, "Configurações", "Em desenvolvimento")
