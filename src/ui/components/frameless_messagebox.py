from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class FramelessMessageBox(QMessageBox):
    def __init__(self, text):
        super(QMessageBox, self).__init__(QMessageBox.NoIcon,'',text,QMessageBox.Ok,None,Qt.FramelessWindowHint)
        self.setStyleSheet("QWidget{}");
        self.exec()
        