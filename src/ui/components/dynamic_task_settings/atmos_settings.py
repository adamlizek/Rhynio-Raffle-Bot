from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import src.ui.settings as SETTINGS
from src.ui.components.form.raffle_dropdown import RaffleDropdown
from src.ui.components.form.gmail_textbox import GmailTextbox
from src.ui.components.form.password_textbox import PasswordTextbox
from src.ui.components.form.plustrick_checkbox import PlustrickCheckbox
from src.ui.components.form.catchall_checkbox import CatchallCheckbox
from src.ui.components.form.catchall_textbox import CatchallTextbox
from src.actions.atmos import atmos_enter_raffle, atmos_confirm_entries, atmos_collect_tokens
from src.utils import populate_raffle_info


class AtmosSettings(QStackedWidget):
    def __init__(self):
        super(QStackedWidget, self).__init__()
        self.init_pages()

    def init_pages(self):
        self.addWidget(self.create_enter_raffle_settings())
        self.addWidget(self.create_collect_token_settings())
        self.addWidget(self.create_confirm_entries_settings())

    def create_enter_raffle_settings(self):
        settings = QWidget()

        layout = QVBoxLayout()
        settings.setLayout(layout)

        layout.setAlignment(Qt.AlignTop)

        # ============================
        # ===== RAFFLE SELECTION =====
        # ============================
        self.raffle_dropdown_enter_raffle = RaffleDropdown()

        raffles = populate_raffle_info.get_active_raffles("ATMOS")
        if raffles.count() == 0:
            self.raffle_dropdown_enter_raffle.raffle_combobox.addItem("No Open Raffles")
        else:
            for raffle in raffles:
                self.raffle_dropdown_enter_raffle.raffle_combobox.addItem(raffle['name'])

        layout.addWidget(self.raffle_dropdown_enter_raffle)

        # =========================
        # ===== GMAIL TEXTBOX =====
        # =========================
        self.gmail_plus_textbox = GmailTextbox()
        self.gmail_enabled = PlustrickCheckbox()

        layout.addWidget(self.gmail_enabled)
        layout.addWidget(self.gmail_plus_textbox)

        # ============================
        # ===== CATCHALL ENABLED =====
        # ============================

        self.catchall_enabled = CatchallCheckbox()
        self.catchall_domain = CatchallTextbox()

        layout.addWidget(self.catchall_enabled)
        layout.addWidget(self.catchall_domain)

        return settings

    def create_collect_token_settings(self):
        settings = QWidget()

        layout = QVBoxLayout()
        settings.setLayout(layout)

        layout.setAlignment(Qt.AlignTop)

        self.raffle_dropdown_collect_tokens = RaffleDropdown()

        # need to add database population here
        raffles = populate_raffle_info.get_active_raffles("ATMOS")
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

        # need to add database population here
        raffles = populate_raffle_info.get_active_raffles("ATMOS")
        if raffles.count() == 0:
            self.raffle_dropdown_confirm_entries.raffle_combobox.addItem("No Open Raffles")
        else:
            for raffle in raffles:
                self.raffle_dropdown_confirm_entries.raffle_combobox.addItem(raffle['name'])

        layout.addWidget(self.raffle_dropdown_confirm_entries)

        return settings

    def refresh(self):
        if SETTINGS.selected_mode == 'ENTER RAFFLE':
            self.setCurrentIndex(0)
        elif SETTINGS.selected_mode == 'COLLECT TOKENS':
            self.setCurrentIndex(1)
        elif SETTINGS.selected_mode == 'CONFIRM ENTRIES':
            self.setCurrentIndex(2)

    def load_task_settings(self):
        selected_raffle = populate_raffle_info.get_specific_raffle("ATMOS",
                                                                   self.raffle_dropdown_enter_raffle.value())

        if SETTINGS.selected_mode == 'ENTER RAFFLE':
            atmos_enter_raffle.ATMOS_RAFFLE_NAME = self.raffle_dropdown_enter_raffle.value().replace(" ", "_")
            atmos_enter_raffle.ATMOS_STORE_ID = selected_raffle['store_id']
            atmos_enter_raffle.ATMOS_RELEASE_ID = selected_raffle['release_id']
            atmos_enter_raffle.ATMOS_PLUSTRICK_ENABLED = self.gmail_enabled.value()
            atmos_enter_raffle.ATMOS_GMAIL = self.gmail_plus_textbox.value()
            atmos_enter_raffle.ATMOS_CATCHALL_ENABLED = self.catchall_enabled.value()
            atmos_enter_raffle.ATMOS_CATCHALL = self.catchall_domain.value()

        if SETTINGS.selected_mode == 'CONFIRM ENTRIES':
            atmos_confirm_entries.ATMOS_RAFFLE_NAME = self.raffle_dropdown_enter_raffle.value().replace(" ", "_")

        if SETTINGS.selected_mode == 'COLLECT TOKENS':
            atmos_collect_tokens.GMAIL_EMAIL = self.gmail_textbox.value()
            atmos_collect_tokens.GMAIL_PASSWORD = self.password_textbox.value()
            atmos_collect_tokens.ATMOS_RAFFLE_NAME = self.raffle_dropdown_collect_tokens.value().replace(" ", "_")
