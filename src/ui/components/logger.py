from pathlib import Path
from PyQt5.QtWidgets import QGridLayout, QApplication, QLabel, QWidget, QTabWidget, QVBoxLayout, QFormLayout, QLineEdit, QHBoxLayout, QRadioButton, QPushButton, QComboBox, QCheckBox, QSpinBox, QMessageBox, QPlainTextEdit, QDialog
import logging
import config as CONFIG


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class Logger(QDialog, QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        logTextBox = QTextEditLogger(self)
        # You can format what is printed to text box
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        # You can control the logging level
        logging.getLogger().setLevel(logging.INFO)

        layout = QVBoxLayout()
        # Add the new logging box widget to the layout
        layout.addWidget(logTextBox.widget)
        self.setLayout(layout)

        with open(str(Path(CONFIG.ROOT, "data/css/main.css")), "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())

        # stylesheet = """
        #     QPlainTextEdit {
        #         background-color: white;
        #         color: black;
        #     }
        # """

        # self.setStyleSheet(stylesheet)