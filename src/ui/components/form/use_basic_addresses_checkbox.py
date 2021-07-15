from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class UseBasicAddressesCheckbox(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.use_basic_addresses = QCheckBox()

        self.stateChanged = self.use_basic_addresses.stateChanged

        layout.addWidget(self.use_basic_addresses)

    def value(self):
        return self.use_basic_addresses.isChecked()