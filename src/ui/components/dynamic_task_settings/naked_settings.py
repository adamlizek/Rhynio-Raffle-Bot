from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import src.ui.settings as SETTINGS
from src.ui.components.form.raffle_dropdown import RaffleDropdown
from src.ui.components.form.country_dropdown import CountryDropdown
from src.ui.components.form.delay_spinbox import DelaySpinbox
from src.ui.components.form.mode_dropdown import ModeDropdown
from src.ui.components.form.custom_password_textbox import PasswordTextbox
from src.ui.components.form.custom_password_checkbox import CustomPasswordCheckbox
from src.actions.naked import naked_enter_raffle, naked_account_gen
from src.utils import populate_raffle_info


class NakedSettings(QStackedWidget):
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
        self.raffle_dropdown = RaffleDropdown()

        soto_raffles = populate_raffle_info.get_active_raffles("NAKED")
        if soto_raffles.count() == 0:
            self.raffle_dropdown.raffle_combobox.addItem("No Open Raffles")
        else:
            for raffle in soto_raffles:
                self.raffle_dropdown.raffle_combobox.addItem(raffle['name'])

        layout.addWidget(self.raffle_dropdown)


        # =============================
        # ===== COUNTRY SELECTION =====
        # =============================
        self.country_dropdown = CountryDropdown()
        layout.addWidget(self.country_dropdown)


        # =================
        # ===== DELAY =====
        # =================
        self.delay_spinbox = DelaySpinbox()
        layout.addWidget(self.delay_spinbox)

        # =================
        # ===== MODE ======
        # =================

        self.entry_mode = ModeDropdown()
        layout.addWidget(self.entry_mode)

        return settings

    def refresh(self):
        if SETTINGS.selected_mode == 'ACCOUNT GENERATION':
            self.setCurrentIndex(0)
        elif SETTINGS.selected_mode == 'ENTER RAFFLE':
            self.setCurrentIndex(1)

    def load_task_settings(self):
        pass
        # LEGACY CODE
        # if SETTINGS.selected_mode == 'ACCOUNT GENERATION':
        #     naked_account_gen.NAKED_CUSTOM_PASSWORD_ENABLED = self.custom_password_enabled.value()
        #     naked_account_gen.NAKED_CUSTOM_PASSWORD = self.custom_password.value()
        #
        # elif SETTINGS.selected_mode == 'ENTER RAFFLE':
        #     naked_enter_raffle.NAKED_RAFFLE_NAME = self.raffle_dropdown.value().replace(" ", "_")
        #     naked_enter_raffle.NAKED_RAFFLE_COUNTRY = self.country_dropdown.value()
        #     naked_enter_raffle.NAKED_ENTRY_DELAY = self.delay_spinbox.value()
        #
        #     selected_raffle = populate_raffle_info.get_specific_raffle("NAKED", self.raffle_dropdown.value())
        #
        #     naked_enter_raffle.NAKED_RAFFLE_WEBPAGE = selected_raffle['webpage_link']
        #     naked_enter_raffle.NAKED_RAFFLE_FORM_ID = selected_raffle['typeform']
        #     naked_enter_raffle.NAKED_RAFFLE_CAPTCHA_TEXT = selected_raffle['captcha1']
        #
        #     naked_enter_raffle.NAKED_FIELD_ID_CAPTCHA = selected_raffle['captcha_id']
        #     naked_enter_raffle.NAKED_FIELD_ID_EMAIL = selected_raffle['email_id']
        #     naked_enter_raffle.NAKED_FIELD_ID_FIRSTNAME = selected_raffle['first_id']
        #     naked_enter_raffle.NAKED_FIELD_ID_LASTNAME = selected_raffle['last_id']
        #     naked_enter_raffle.NAKED_FIELD_ID_ADDRESS1 = selected_raffle['address_1_id']
        #     naked_enter_raffle.NAKED_FIELD_ID_ADDRESS2 = selected_raffle['address_2_id']
        #     naked_enter_raffle.NAKED_FIELD_ID_CITY = selected_raffle['city_id']
        #     naked_enter_raffle.NAKED_FIELD_ID_PHONE = selected_raffle['phone_id']
        #     naked_enter_raffle.NAKED_FIELD_ID_ZIPCODE = selected_raffle['zip_id']
        #     naked_enter_raffle.NAKED_FIELD_ID_COUNTRY = selected_raffle['country_id']
        #     naked_enter_raffle.NAKED_FIELD_ID_NEWSLETTER = selected_raffle['newsletter_id']
        #
        #     if self.entry_mode.value() == 'Extra Safe':
        #         naked_enter_raffle.NAKED_ENTRY_LEVEL = 1
        #     elif self.entry_mode.value() == 'Normal':
        #         naked_enter_raffle.NAKED_ENTRY_LEVEL = 2
        #     elif self.entry_mode.value() == 'Risky':
        #         naked_enter_raffle.NAKED_ENTRY_LEVEL = 3
