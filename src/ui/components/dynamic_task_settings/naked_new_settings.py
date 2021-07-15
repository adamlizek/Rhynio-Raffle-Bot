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
from src.actions.naked_new import naked_enter_raffle, naked_account_gen, naked_collect_tokens, naked_email_confirmation
from src.utils import populate_raffle_info
from src.ui.components.form.gmail_textbox import GmailTextbox
from src.ui.components.form.password_textbox import PasswordTextbox
from src.ui.components.form.overwrite_saved_addresses_checkbox import OverwriteAddressCheckbox


class NewNakedSettings(QStackedWidget):
    def __init__(self):
        super(QStackedWidget, self).__init__()
        self.init_pages()
    
    def init_pages(self):
        self.addWidget(self.create_account_gen_settings())
        self.addWidget(self.create_enter_raffle_settings())
        self.addWidget(self.create_collect_token_settings())
        self.addWidget(self.create_confirm_entries_settings())

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
        raffles = populate_raffle_info.get_active_raffles("NEWNAKED")
        if raffles.count() == 0:
            self.raffle_dropdown_enter_raffle.raffle_combobox.addItem("No Open Raffles")
        else:
            for raffle in raffles:
                self.raffle_dropdown_enter_raffle.raffle_combobox.addItem(raffle['name'])
        layout.addWidget(self.raffle_dropdown_enter_raffle)


        # =============================
        # ===== COUNTRY SELECTION =====
        # =============================
        self.country_dropdown = CountryDropdown()
        layout.addWidget(self.country_dropdown)


        # =================
        # ===== MODE ======
        # =================

        self.entry_mode = ModeDropdown()
        layout.addWidget(self.entry_mode)

        # ================================
        # ===== OVERWRITE ADDRESSES ======
        # ================================

        self.overwrite_enabled = OverwriteAddressCheckbox()
        layout.addWidget(self.overwrite_enabled)

        return settings

    def create_collect_token_settings(self):
        settings = QWidget()

        layout = QVBoxLayout()
        settings.setLayout(layout)

        layout.setAlignment(Qt.AlignTop)


        # ============================
        # ===== RAFFLE SELECTION =====
        # ============================
        self.raffle_dropdown_collect_tokens = RaffleDropdown()
        raffles = populate_raffle_info.get_active_raffles("NEWNAKED")
        if raffles.count() == 0:
            self.raffle_dropdown_collect_tokens.raffle_combobox.addItem("No Open Raffles")
        else:
            for raffle in raffles:
                self.raffle_dropdown_collect_tokens.raffle_combobox.addItem(raffle['name'])
        layout.addWidget(self.raffle_dropdown_collect_tokens)


        # =========================
        # ===== GMAIL TEXTBOX =====
        # =========================
        self.gmail_textbox = GmailTextbox()
        layout.addWidget(self.gmail_textbox)


        # ============================
        # ===== PASSWORD TEXTBOX =====
        # ============================
        self.password_textbox = PasswordTextbox()
        layout.addWidget(self.password_textbox)

        return settings

    def create_confirm_entries_settings(self):
        settings = QWidget()

        layout = QVBoxLayout()
        settings.setLayout(layout)

        layout.setAlignment(Qt.AlignTop)


        # ============================
        # ===== RAFFLE SELECTION =====
        # ============================
        self.raffle_dropdown_confirm_entries = RaffleDropdown()
        raffles = populate_raffle_info.get_active_raffles("NEWNAKED")
        if raffles.count() == 0:
            self.raffle_dropdown_confirm_entries.raffle_combobox.addItem("No Open Raffles")
        else:
            for raffle in raffles:
                self.raffle_dropdown_confirm_entries.raffle_combobox.addItem(raffle['name'])
        layout.addWidget(self.raffle_dropdown_confirm_entries)

        return settings

    def refresh(self):
        if SETTINGS.selected_mode == 'ACCOUNT GENERATION':
            self.setCurrentIndex(0)
        elif SETTINGS.selected_mode == 'ENTER RAFFLE':
            self.setCurrentIndex(1)
        elif SETTINGS.selected_mode == 'COLLECT TOKENS':
            self.setCurrentIndex(2)
        elif SETTINGS.selected_mode == 'CONFIRM ENTRIES':
            self.setCurrentIndex(3)

    def load_task_settings(self):
        if SETTINGS.selected_mode == 'ACCOUNT GENERATION':
            naked_account_gen.NAKED_CUSTOM_PASSWORD_ENABLED = self.custom_password_enabled.value()
            naked_account_gen.NAKED_CUSTOM_PASSWORD = self.custom_password.value()

        elif SETTINGS.selected_mode == 'ENTER RAFFLE':
            naked_enter_raffle.NAKED_RAFFLE_NAME = self.raffle_dropdown_enter_raffle.value().replace(" ", "_")
            naked_enter_raffle.NAKED_RAFFLE_COUNTRY = self.country_dropdown.value()

            selected_raffle = populate_raffle_info.get_specific_raffle("NEWNAKED", self.raffle_dropdown_enter_raffle.value())
            naked_enter_raffle.NAKED_RAFFLE_WEBPAGE = selected_raffle['webpage']
            naked_enter_raffle.NAKED_RAFFLE_TAGS = selected_raffle['tags']
            naked_enter_raffle.NAKED_RAFFLE_TOKEN = selected_raffle['token']

            print(self.overwrite_enabled.value())
            naked_enter_raffle.NAKED_OVERWRITE_ADDRESS = self.overwrite_enabled.value()


            if self.entry_mode.value() == 'Extra Safe':
                naked_enter_raffle.NAKED_ENTRY_LEVEL = 1
            elif self.entry_mode.value() == 'Normal':
                naked_enter_raffle.NAKED_ENTRY_LEVEL = 2
            elif self.entry_mode.value() == 'Risky':
                naked_enter_raffle.NAKED_ENTRY_LEVEL = 3

        elif SETTINGS.selected_mode == 'COLLECT TOKENS':
            naked_collect_tokens.GMAIL_EMAIL = self.gmail_textbox.value()
            naked_collect_tokens.GMAIL_PASSWORD = self.password_textbox.value()
            naked_collect_tokens.NAKED_RAFFLE_NAME = self.raffle_dropdown_collect_tokens.value().replace(" ", "_")

        elif SETTINGS.selected_mode == 'CONFIRM ENTRIES':
            naked_email_confirmation.NAKED_RAFFLE_NAME = self.raffle_dropdown_confirm_entries.value().replace(" ", "_")
