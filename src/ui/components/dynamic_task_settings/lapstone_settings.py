from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import src.ui.settings as SETTINGS
from src.ui.components.form.raffle_dropdown import RaffleDropdown
from src.ui.components.form.gmail_textbox import GmailTextbox
from src.ui.components.form.password_textbox import PasswordTextbox
from src.actions.lapstone import lapstone_collect_tokens, lapstone_email_confirmation, lapstone_enter_raffle
from src.utils import populate_raffle_info
import config as CONFIG


class LapstoneSettings(QStackedWidget):
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

        layout.addWidget(QLabel("Lapstone Cookie Generation (Browser Based)"))

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

        raffles = populate_raffle_info.get_active_raffles("LAPSTONE")
        if raffles.count() == 0:
            self.raffle_dropdown_enter_raffle.raffle_combobox.addItem("No Open Raffles")
        else:
            for raffle in raffles:
                self.raffle_dropdown_enter_raffle.raffle_combobox.addItem(raffle['name'])

        layout.addWidget(self.raffle_dropdown_enter_raffle)
        return settings
    
    def create_collect_token_settings(self):
        settings = QWidget()

        layout = QVBoxLayout()
        settings.setLayout(layout)

        layout.setAlignment(Qt.AlignTop)

        self.raffle_dropdown_collect_tokens = RaffleDropdown()

        # need to add database population here
        raffles = populate_raffle_info.get_active_raffles("LAPSTONE")
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
        raffles = populate_raffle_info.get_active_raffles("LAPSTONE")
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
        selected_raffle = populate_raffle_info.get_specific_raffle("LAPSTONE", self.raffle_dropdown_enter_raffle.value())

        if SETTINGS.selected_mode == 'ENTER RAFFLE':
            lapstone_enter_raffle.LAPSTONE_RAFFLE_NAME = self.raffle_dropdown_enter_raffle.value().replace(" ", "_")
            selected_raffle = populate_raffle_info.get_specific_raffle("LAPSTONE",
                                                                       self.raffle_dropdown_enter_raffle.value())
            lapstone_enter_raffle.LAPSTONE_RAFFLE_URL = selected_raffle['url']
            lapstone_enter_raffle.LAPSTONE_RAFFLE_U = selected_raffle['u']
            lapstone_enter_raffle.LAPSTONE_RAFFLE_ID = selected_raffle['id']
            lapstone_enter_raffle.LAPSTONE_RAFFLE_FAKE_PARAM = selected_raffle['fake_param']
            lapstone_enter_raffle.LAPSTONE_ANSWER = selected_raffle['answer']

        elif SETTINGS.selected_mode == 'COLLECT TOKENS':
            lapstone_collect_tokens.GMAIL_EMAIL = self.gmail_textbox.value()
            lapstone_collect_tokens.GMAIL_PASSWORD = self.password_textbox.value()
            lapstone_collect_tokens.LAPSTONE_RAFFLE_NAME = self.raffle_dropdown_collect_tokens.value().replace(" ", "_")

        elif SETTINGS.selected_mode == 'CONFIRM ENTRIES':
            lapstone_email_confirmation.LAPSTONE_RAFFLE_NAME = self.raffle_dropdown_confirm_entries.value().replace(" ", "_")
            lapstone_email_confirmation.LAPSTONE_RAFFLE_U = selected_raffle['u']
            lapstone_email_confirmation.LAPSTONE_RAFFLE_ID = selected_raffle['id']
