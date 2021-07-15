from pathlib import Path
import config as CONFIG
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from src.ui import interface
import sys

app = QApplication([])
app.setWindowIcon(QIcon(str(Path(CONFIG.ROOT, "data/assets/icons.icon"))))
interface = interface.Interface()
interface.setWindowIcon(QIcon(str(Path(CONFIG.ROOT, "data/assets/icons.ico"))))
sys.exit(app.exec_())