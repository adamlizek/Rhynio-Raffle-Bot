from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import src.ui.settings as SETTINGS
from src.ui.components.form.raffle_dropdown import RaffleDropdown
from src.ui.components.form.gmail_textbox import GmailTextbox
from src.ui.components.form.password_textbox import PasswordTextbox
from src.ui.components.form.plustrick_checkbox import PlustrickCheckbox
from src.actions.dtlr import dtlr_collect_tokens, dtlr_confirm_entries, dtlr_enter_raffle
from src.utils import populate_raffle_info


class DTLRSettings(QStackedWidget):
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

        raffles = populate_raffle_info.get_active_raffles("DTLR")
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

        return settings

    def create_collect_token_settings(self):
        settings = QWidget()

        layout = QVBoxLayout()
        settings.setLayout(layout)

        layout.setAlignment(Qt.AlignTop)

        self.raffle_dropdown_collect_tokens = RaffleDropdown()

        raffles = populate_raffle_info.get_active_raffles("DTLR")
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

        raffles = populate_raffle_info.get_active_raffles("DTLR")
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
        if SETTINGS.selected_mode == 'ENTER RAFFLE':
            dtlr_enter_raffle.DTLR_RAFFLE_NAME = self.raffle_dropdown_enter_raffle.value().replace(" ", "_")

            selected_raffle = populate_raffle_info.get_specific_raffle("DTLR", self.raffle_dropdown_enter_raffle.value())

            dtlr_enter_raffle.DTLR_RAFFLE_NUMBER = selected_raffle['raffle_number']
            dtlr_enter_raffle.DTLR_RAFFLE_URL = selected_raffle['webpage_link']
            dtlr_enter_raffle.DTLR_GS_SIZING = selected_raffle['gs']

            dtlr_enter_raffle.DTLR_PLUSTRICK_ENABLED = self.gmail_plus_textbox.value()
            dtlr_enter_raffle.DTLR_GMAIL = self.gmail_plus_textbox.value()

        elif SETTINGS.selected_mode == 'COLLECT TOKENS':
            dtlr_collect_tokens.GMAIL_EMAIL = self.gmail_textbox.value()
            dtlr_collect_tokens.GMAIL_PASSWORD = self.password_textbox.value()
            dtlr_collect_tokens.DTLR_RAFFLE_NAME = self.raffle_dropdown_collect_tokens.value().replace(" ", "_")

        elif SETTINGS.selected_mode == 'CONFIRM ENTRIES':
            dtlr_confirm_entries.DTLR_RAFFLE_NAME = self.raffle_dropdown_confirm_entries.value().replace(" ", "_")
