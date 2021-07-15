from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import src.ui.settings as SETTINGS
from src.ui.components.form.raffle_dropdown import RaffleDropdown
from src.ui.components.form.gmail_textbox import GmailTextbox
from src.ui.components.form.plustrick_checkbox import PlustrickCheckbox
from src.ui.components.form.catchall_checkbox import CatchallCheckbox
from src.ui.components.form.catchall_textbox import CatchallTextbox
from src.actions.bodega import bodega_enter_raffle
from src.utils import populate_raffle_info


class BodegaSettings(QStackedWidget):
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
        self.raffle_dropdown = RaffleDropdown()

        soto_raffles = populate_raffle_info.get_active_raffles("BODEGA")
        if soto_raffles.count() == 0:
            self.raffle_dropdown.raffle_combobox.addItem("No Open Raffles")
        else:
            for raffle in soto_raffles:
                self.raffle_dropdown.raffle_combobox.addItem(raffle['name'])

        layout.addWidget(self.raffle_dropdown)

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
        bodega_enter_raffle.BODEGA_RAFFLE_NAME = self.raffle_dropdown.value().replace(" ", "_")

        bodega_enter_raffle.BODEGA_PLUSTRICK_ENABLED = self.gmail_enabled.value()
        bodega_enter_raffle.BODEGA_GMAIL = self.gmail_plus_textbox.value()
        bodega_enter_raffle.BODEGA_CATCHALL_ENABLED = self.catchall_enabled.value()
        bodega_enter_raffle.BODEGA_CATCHALL = self.catchall_domain.value()

        selected_raffle = populate_raffle_info.get_specific_raffle("BODEGA", self.raffle_dropdown.value())

        bodega_enter_raffle.BODEGA_RAFFLE_URL = selected_raffle['url']
        bodega_enter_raffle.BODEGA_RAFFLE_WEBPAGE = selected_raffle['webpage']
        bodega_enter_raffle.BODEGA_PID = selected_raffle['pid']
        bodega_enter_raffle.BODEGA_RNDID = selected_raffle['rndid']
        bodega_enter_raffle.BODEGA_POST_ID = selected_raffle['post_id']
        bodega_enter_raffle.BODEGA_SIZE_ID = selected_raffle['size_id']
        bodega_enter_raffle.BODEGA_REFERER_HEADER = selected_raffle['referer']
        bodega_enter_raffle.BODEGA_INSTAGRAM_ID = selected_raffle['instagram_id']
        bodega_enter_raffle.BODEGA_STYLE = selected_raffle['style']
        bodega_enter_raffle.BODEGA_STYLE_ID = selected_raffle['style_id']
