from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import src.ui.settings as SETTINGS
from src.ui.components.form.raffle_dropdown import RaffleDropdown
from src.ui.components.form.gmail_textbox import GmailTextbox
from src.ui.components.form.plustrick_checkbox import PlustrickCheckbox
from src.ui.components.form.catchall_checkbox import CatchallCheckbox
from src.ui.components.form.catchall_textbox import CatchallTextbox
from src.actions.undefeated import undefeated_enter_raffle
from src.utils import populate_raffle_info


class UndefeatedSettings(QStackedWidget):
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
        self.raffle_dropdown_enter_raffle = RaffleDropdown()

        raffles = populate_raffle_info.get_active_raffles("UNDEFEATED")
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

    def refresh(self):
        self.setCurrentIndex(0)


    def load_task_settings(self):
        selected_raffle = populate_raffle_info.get_specific_raffle("UNDEFEATED", self.raffle_dropdown_enter_raffle.value())
        
        undefeated_enter_raffle.UNDEFEATED_RAFFLE_NAME = self.raffle_dropdown_enter_raffle.value().replace(" ", "_")
        undefeated_enter_raffle.UNDEFEATED_RAFFLE_WEBPAGE = selected_raffle['webpage']
        undefeated_enter_raffle.UNDEFEATED_RAFFLE_URL = selected_raffle['viral_url']
        undefeated_enter_raffle.UNDEFEATED_PID = selected_raffle['pid']
        undefeated_enter_raffle.UNDEFEATED_RNDID = selected_raffle['rndid']
        undefeated_enter_raffle.UNDEFEATED_POST_ID = selected_raffle['post_id']
        undefeated_enter_raffle.UNDEFEATED_QUESTION_ANSWER = selected_raffle['answer']
        undefeated_enter_raffle.UNDEFEATED_STYLE = selected_raffle['style']

        undefeated_enter_raffle.UNDEFEATED_PLUSTRICK_ENABLED = self.gmail_enabled.value()
        undefeated_enter_raffle.UNDEFEATED_GMAIL = self.gmail_plus_textbox.value()
        undefeated_enter_raffle.UNDEFEATED_CATCHALL_ENABLED = self.catchall_enabled.value()
        undefeated_enter_raffle.UNDEFEATED_CATCHALL = self.catchall_domain.value()
