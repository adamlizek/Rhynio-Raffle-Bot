from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import config as CONFIG


class Navbar(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setObjectName('Navbar')

        self.setup_icon()
        self.setup_buttons()

        with open(str(Path(CONFIG.ROOT, "data/css/navbar.css")), "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())

        # stylesheet = """
        #     QPushButton {
        #         background-color: transparent;
        #         color: white;
        #         font-size: 18px;
        #         font-weight: 600;
        #     }

        #     QPushButton::hover {
        #         color: #ec7200;
        #     }

        #     QPushButton:focus:hover{
        #         color: white;
        #     }
            
        #     QPushButton:focus:pressed{ background-color: black; }
            
        #     QPushButton:focus{ 
        #     background-color: #ec7200;
        #     border: 1px solid #ec7200; }

        #     QLabel#logo {
        #         margin-bottom: 20px;
        #         margin-top: 10px;
        #         margin-left: 10px;
        #     }
        # """

        # self.setStyleSheet(stylesheet)

        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def setup_buttons(self):
        self.main_page_btn = QPushButton("Main")
        self.main_page_btn.clicked.connect(
            self.parent().page_manager.open_main_page)

        self.task_setup_page_btn = QPushButton("Task Setup")
        self.task_setup_page_btn.clicked.connect(
            self.parent().page_manager.open_task_setup_page)

        # self.raffles_page_btn = QPushButton("Raffles")
        # self.raffles_page_btn.clicked.connect(self.parent().page_manager.open_raffles_page)

        self.proxies_page_btn = QPushButton("Proxies")
        self.proxies_page_btn.clicked.connect(
            self.parent().page_manager.open_proxies_page)

        self.emails_page_btn = QPushButton("Emails")
        self.emails_page_btn.clicked.connect(
            self.parent().page_manager.open_emails_page)

        # self.entry_information_page_btn = QPushButton("Entry Information")
        # self.entry_information_page_btn.clicked.connect(self.parent().page_manager.open_entry_information_page)

        # self.accounts_page_btn = QPushButton("Accounts")
        # self.accounts_page_btn.clicked.connect(self.parent().page_manager.open_accounts_page)

        self.settings_page_btn = QPushButton("Settings")
        self.settings_page_btn.clicked.connect(
            self.parent().page_manager.open_settings_page)

        self.layout.addWidget(self.main_page_btn)
        self.layout.addWidget(self.task_setup_page_btn)
        # self.layout.addWidget(self.raffles_page_btn)
        self.layout.addWidget(self.proxies_page_btn)
        self.layout.addWidget(self.emails_page_btn)
        # self.layout.addWidget(self.entry_information_page_btn)
        # self.layout.addWidget(self.accounts_page_btn)
        self.layout.addWidget(self.settings_page_btn)

    def setup_icon(self):
        icon = QLabel(self)

        pixmap = QPixmap(str(Path(CONFIG.ROOT, "data/assets/rhynio_header.png")))
        icon.setPixmap(pixmap)

        icon.resize(180, 60)
        icon.setPixmap(pixmap.scaled(icon.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation))

        icon.setObjectName('logo')

        self.layout.addWidget(icon)
