from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class DelaySpinbox(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Delay"), 1)

        self.delay_spinbox = QSpinBox()
        self.delay_spinbox.setValue(50)
        layout.addWidget(self.delay_spinbox, 2)

    def value(self):
        return self.delay_spinbox.value()