from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class CustomZipcodeCheckbox(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Enable Custom Zipcode"), 1)

        self.custom_zipcode_enabled = QCheckBox()
        layout.addWidget(self.custom_zipcode_enabled, 2)

    def value(self):
        return self.custom_zipcode_enabled.isChecked()