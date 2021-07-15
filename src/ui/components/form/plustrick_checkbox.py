from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class PlustrickCheckbox(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Enable Plus Trick Entry"), 1)

        self.catchall_enabled = QCheckBox()

        self.stateChanged = self.catchall_enabled.stateChanged

        layout.addWidget(self.catchall_enabled, 2)

    def value(self):
        return self.catchall_enabled.isChecked()
