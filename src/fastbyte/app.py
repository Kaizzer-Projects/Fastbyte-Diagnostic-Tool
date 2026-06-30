import sys
from PyQt5.QtWidgets import QApplication
from fastbyte.main_window import MainWindow


def run():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
