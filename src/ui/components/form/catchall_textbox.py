from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class CatchallTextbox(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Catchall Domain"), 1)

        self.catchall_domain = QLineEdit()
        layout.addWidget(self.catchall_domain, 2)

    def value(self):
        return self.catchall_domain.text()