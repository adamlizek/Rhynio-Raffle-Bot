from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class CaptchaSolverDropdown(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.captcha_solver_combobox = QComboBox()
        self.captcha_solver_combobox.addItem("2Captcha")
        self.captcha_solver_combobox.addItem("AntiCaptcha")
        self.captcha_solver_combobox.addItem("Capmonster")
        layout.addWidget(self.captcha_solver_combobox)

    def value(self):
        return self.captcha_solver_combobox.currentText()

    def setIndex(self, index):
        self.captcha_solver_combobox.setCurrentIndex(index)
