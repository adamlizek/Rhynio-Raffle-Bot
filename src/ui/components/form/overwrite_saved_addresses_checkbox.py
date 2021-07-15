from PyQt5.QtWidgets import *


class OverwriteAddressCheckbox(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Overwrite Saved Addresses"), 1)
        self.overwriteEnabled = QCheckBox()
        self.stateChanged = self.overwriteEnabled.stateChanged

        layout.addWidget(self.overwriteEnabled, 2)

    def value(self):
        return self.overwriteEnabled.isChecked()
