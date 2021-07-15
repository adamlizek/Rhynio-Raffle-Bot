from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class GmailTextbox(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Gmail"), 1)

        self.gmail_textbox = QLineEdit()
        layout.addWidget(self.gmail_textbox, 2)

    def value(self):
        return self.gmail_textbox.text()