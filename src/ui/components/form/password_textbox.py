from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class PasswordTextbox(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Password"), 1)

        self.password_textbox = QLineEdit()
        layout.addWidget(self.password_textbox, 2)

    def value(self):
        return self.password_textbox.text()