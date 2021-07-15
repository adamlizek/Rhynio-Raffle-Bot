from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class PasswordTextbox(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Custom Password"), 1)

        self.custom_password = QLineEdit()
        layout.addWidget(self.custom_password, 2)

    def value(self):
        return self.custom_password.text()