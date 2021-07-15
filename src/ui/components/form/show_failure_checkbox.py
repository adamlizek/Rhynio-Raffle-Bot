from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class ShowFailureCheckbox(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.show_failure_enabled = QCheckBox()

        self.stateChanged = self.show_failure_enabled.stateChanged

        layout.addWidget(self.show_failure_enabled)

    def value(self):
        return self.show_failure_enabled.isChecked()