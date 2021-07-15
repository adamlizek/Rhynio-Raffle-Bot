from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import src.ui.settings as SETTINGS
from src.ui.components.form.raffle_dropdown import RaffleDropdown
from src.ui.components.form.catchall_checkbox import CatchallCheckbox
from src.ui.components.form.catchall_textbox import CatchallTextbox
from src.actions.travis import travis_enter_raffle

class TravisSettings(QStackedWidget):
    def __init__(self):
        super(QStackedWidget, self).__init__()
        self.init_pages()

    def init_pages(self):
        self.addWidget(self.create_enter_raffle_settings())

    def create_enter_raffle_settings(self):
        settings = QWidget()

        layout = QVBoxLayout()
        settings.setLayout(layout)

        layout.setAlignment(Qt.AlignTop)

        # ============================
        # ===== RAFFLE SELECTION =====
        # ============================
        # ============================
        # ===== RAFFLE SELECTION =====
        # ============================
        self.raffle_dropdown = RaffleDropdown()
        self.raffle_dropdown.raffle_combobox.addItem("ITS LIT")

        layout.addWidget(self.raffle_dropdown)

        # ============================
        # ===== CATCHALL ENABLED =====
        # ============================

        self.catchall_enabled = CatchallCheckbox()
        self.catchall_domain = CatchallTextbox()

        layout.addWidget(self.catchall_enabled)
        layout.addWidget(self.catchall_domain)

        return settings

    def refresh(self):
        self.setCurrentIndex(0)

    def load_task_settings(self):
        travis_enter_raffle.TRAVIS_RAFFLE_NAME = self.raffle_dropdown.value().replace(" ", "_")

        travis_enter_raffle.TRAVIS_CATCHALL_ENABLED = self.catchall_enabled.value()
        travis_enter_raffle.TRAVIS_CATCHALL = self.catchall_domain.value()
