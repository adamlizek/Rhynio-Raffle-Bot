from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class CountryDropdown(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)
        
        layout.addWidget(QLabel("Country"), 1)

        self.country_combobox = QComboBox()
        layout.addWidget(self.country_combobox, 2)

        self.country_combobox.addItem("United States")
        self.country_combobox.addItem("Denmark")
        self.country_combobox.addItem("Germany")
        self.country_combobox.addItem("United Kingdom")
        self.country_combobox.addItem("France")
        self.country_combobox.addItem("Spain")
        self.country_combobox.addItem("Portugal")
        self.country_combobox.addItem("Romania")
        self.country_combobox.addItem("Norway")
        self.country_combobox.addItem("Sweden")
        self.country_combobox.addItem("Random")

    def value(self):
        return self.country_combobox.currentText()