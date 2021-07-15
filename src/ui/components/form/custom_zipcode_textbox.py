from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class ZipcodeTextbox(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Custom Zipcode"), 1)

        self.custom_zipcode = QLineEdit()
        layout.addWidget(self.custom_zipcode, 2)

    def value(self):
        return self.custom_zipcode.text()