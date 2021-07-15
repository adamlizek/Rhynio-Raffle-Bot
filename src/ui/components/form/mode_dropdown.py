from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class ModeDropdown(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Entry Mode"), 1)

        self.mode_dropdown = QComboBox()
        layout.addWidget(self.mode_dropdown, 2)

        self.mode_dropdown.addItem("Normal")
        self.mode_dropdown.addItem("Extra Safe")
        self.mode_dropdown.addItem("Risky")

    def value(self):
        return self.mode_dropdown.currentText()
