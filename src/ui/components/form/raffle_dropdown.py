from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class RaffleDropdown(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Raffle"), 1)

        self.raffle_combobox = QComboBox()
        layout.addWidget(self.raffle_combobox, 2)

    def value(self):
        return self.raffle_combobox.currentText()