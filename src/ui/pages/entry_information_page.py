from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class EntryInformationPage(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        self.layout = QVBoxLayout(self)

        self.pushButton1 = QPushButton("Entry Information Page")
        self.layout.addWidget(self.pushButton1)
        self.setLayout(self.layout)