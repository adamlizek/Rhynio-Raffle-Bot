from pathlib import Path
import sys
import config as CONFIG
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.ui.components.titlebar import TitleBar
from src.ui.components.managers.page_manager import PageManager
from src.ui.components.navbar import Navbar


class Interface(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__()
        self.init_properties()

        # we need to init ALL components first as some rely on others
        # then we can align them in the order we want
        self.init_components()
        self.align_components()
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.show()

    def init_properties(self):
        self.WIDTH = 1000
        self.HEIGHT = 666
        
        self.setWindowTitle(CONFIG.RHYNIO_VERSION)
        self.setGeometry(0, 0, self.WIDTH, self.HEIGHT)
        
        # print('1 ' + os.path.dirname(sys.executable))
        # print('2 ' + os.path.dirname(__file__))
        # print('3 ' + os.getcwd())
        # print('4 ' + CONFIG.ROOT)
        # print('5 ' + os.path.join(CONFIG.ROOT, "data/css/main.css"))
        # print('6 ' + str(Path(os.path.join(CONFIG.ROOT, "data/css/main.css"))))
        # print('7 ' + str(Path(CONFIG.ROOT, "data/css/main.css")))


        with open(str(Path(CONFIG.ROOT, "data/css/main.css")), "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())

        # stylesheet = """
        #     QMainWindow {
        #         padding: none;
        #         margin: none;
        #     }
            
        #     QMainWindow QWidget {
        #         border: none;
        #     }            
        # """

        # self.setStyleSheet(stylesheet)

    def init_components(self):
        self.window_widget = QWidget()
        self.central_widget = QWidget()
        self.titlebar = TitleBar(self)
        self.page_manager = PageManager()
        self.page_manager.setObjectName("page_manager")
        self.navbar = Navbar(self)
        
    def align_components(self):
        layout1 = QVBoxLayout()
        layout1.setAlignment(Qt.AlignTop)
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        
        
        layout1.setSpacing(0)
        layout.setSpacing(0)
        layout1.setContentsMargins(0,0,0,0)
        layout.setContentsMargins(0,0,0,0)
        
        
        layout.addWidget(self.navbar, 0)
        layout.addWidget(self.page_manager, 0)
        self.central_widget.setLayout(layout)
        
        layout1.addWidget(self.titlebar, 0)
        layout1.addWidget(self.central_widget, 0)
        self.window_widget.setLayout(layout1)

        
        self.setCentralWidget(self.window_widget)
        
    def showSmall(self):
        self.showMinimized()

    def showMaxRestore(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
