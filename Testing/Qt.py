#/!/usr/bin/python
#https://realpython.com/python-pyqt-gui-calculator/#installing-pyqt
import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

app = QApplication([])

window = QWidget()
window.setWindowTitle("test")
window.setGeometry(100, 100, 280, 80)
helloMsg = QLabel("Hello world", parent = window)
helloMsg.move (60,15)

window.show()

sys.exit(app.exec())