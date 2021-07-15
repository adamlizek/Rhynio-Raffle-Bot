from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import src.ui.settings as SETTINGS
from src.ui.components.form.raffle_dropdown import RaffleDropdown
from src.ui.components.form.custom_password_textbox import PasswordTextbox
from src.ui.components.form.custom_password_checkbox import CustomPasswordCheckbox
from src.actions.sjs import sjs_enter_raffle, sjs_account_gen
from src.utils import populate_raffle_info


class SJSSettings(QStackedWidget):
    def __init__(self):
        super(QStackedWidget, self).__init__()
        self.init_pages()

    def init_pages(self):
        self.addWidget(self.create_account_gen_settings())
        self.addWidget(self.create_enter_raffle_settings())

    def create_account_gen_settings(self):
        settings = QWidget()

        layout = QVBoxLayout()
        settings.setLayout(layout)

        layout.setAlignment(Qt.AlignTop)

        # ============================
        # ===== CUSTOM PASSWORD  =====
        # ============================

        self.custom_password_enabled = CustomPasswordCheckbox()
        self.custom_password = PasswordTextbox()

        layout.addWidget(self.custom_password_enabled)
        layout.addWidget(self.custom_password)

        return settings

    def create_enter_raffle_settings(self):
        settings = QWidget()

        layout = QVBoxLayout()
        settings.setLayout(layout)

        layout.setAlignment(Qt.AlignTop)

        # ============================
        # ===== RAFFLE SELECTION =====
        # ============================
        self.raffle_dropdown_enter_raffle = RaffleDropdown()
        raffles = populate_raffle_info.get_active_raffles("SJS")
        if raffles.count() == 0:
            self.raffle_dropdown_enter_raffle.raffle_combobox.addItem("No Open Raffles")
        else:
            for raffle in raffles:
                self.raffle_dropdown_enter_raffle.raffle_combobox.addItem(raffle['name'])
        layout.addWidget(self.raffle_dropdown_enter_raffle)

        return settings

    def refresh(self):
        if SETTINGS.selected_mode == 'ACCOUNT GENERATION':
            self.setCurrentIndex(0)
        elif SETTINGS.selected_mode == 'ENTER RAFFLE':
            self.setCurrentIndex(1)

    def load_task_settings(self):
        if SETTINGS.selected_mode == 'ACCOUNT GENERATION':
            sjs_account_gen.SJS_CUSTOM_PASSWORD_ENABLED = self.custom_password_enabled.value()
            sjs_account_gen.SJS_CUSTOM_PASSWORD = self.custom_password.value()

        elif SETTINGS.selected_mode == 'ENTER RAFFLE':
            sjs_enter_raffle.SJS_RAFFLE_NAME = self.raffle_dropdown_enter_raffle.value().replace(" ", "_")

            selected_raffle = populate_raffle_info.get_specific_raffle("SJS",
                                                                       self.raffle_dropdown_enter_raffle.value())
            sjs_enter_raffle.SJS_RAFFLE_URL = selected_raffle['raffle_url']
            sjs_enter_raffle.SJS_VARIANTS = selected_raffle['variants']
