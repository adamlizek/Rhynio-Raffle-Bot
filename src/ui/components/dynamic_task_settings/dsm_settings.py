from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import src.ui.settings as SETTINGS
from src.ui.components.form.raffle_dropdown import RaffleDropdown
from src.ui.components.form.gmail_textbox import GmailTextbox
from src.ui.components.form.plustrick_checkbox import PlustrickCheckbox
from src.ui.components.form.catchall_checkbox import CatchallCheckbox
from src.ui.components.form.catchall_textbox import CatchallTextbox
from src.actions.dsm import dsm_enter_raffle
from src.utils import populate_raffle_info
import config as CONFIG


class DSMSettings(QStackedWidget):
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

        raffles = populate_raffle_info.get_active_raffles("DSM")
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

        self.gmail_enabled.stateChanged.connect(self.onStateChange)

        layout.addWidget(self.gmail_enabled)
        layout.addWidget(self.gmail_plus_textbox)

        # ============================
        # ===== CATCHALL ENABLED =====
        # ============================

        self.catchall_enabled = CatchallCheckbox()
        self.catchall_domain = CatchallTextbox()

        self.catchall_enabled.stateChanged.connect(self.onStateChange)

        layout.addWidget(self.catchall_enabled)
        layout.addWidget(self.catchall_domain)

        return settings

    def refresh(self):
        self.setCurrentIndex(0)

    #https://stackoverflow.com/questions/48399579/python-pyqt-checkbox-to-uncheck-all-other-checkboxes
    @pyqtSlot(int)
    def onStateChange(self, state):
        if state == Qt.Checked:
            if self.sender() == self.catchall_enabled:
                self.gmail_enabled.setChecked(False)
            elif self.sender() == self.gmail_enabled:
                self.catchall_enabled.setChecked(False)
            else:
                print(str(self.sender()))
                print(str(self.catchall_enabled))

    def load_task_settings(self):
        #DSM_enter_raffle.DTLR_RAFFLE_NAME = self.raffle_dropdown_enter_raffle.value().replace(" ", "_") Wait until after raffle and uncomment this
        
        selected_raffle = populate_raffle_info.get_specific_raffle("DSM", self.raffle_dropdown_enter_raffle.value())

        dsm_enter_raffle.DSM_RAFFLE_URL = selected_raffle['raffle_url']
        dsm_enter_raffle.DSM_SUCCESS_URL = selected_raffle['success_url']
        dsm_enter_raffle.DSM_FORMSTACK_URL = selected_raffle['formstack_url']
        dsm_enter_raffle.DSM_RAFFLE_NAME = selected_raffle['name'].replace(" ", "_")
        dsm_enter_raffle.DSM_NAME_ID = selected_raffle['name_id']
        dsm_enter_raffle.DSM_EMAIL_ID = selected_raffle['email_id']
        dsm_enter_raffle.DSM_PHONE_ID = selected_raffle['phone_id']
        dsm_enter_raffle.DSM_SIZE_ID = selected_raffle['size_id']
        dsm_enter_raffle.DSM_ADDRESS1_ID = selected_raffle['address1_id']
        dsm_enter_raffle.DSM_STATE_ID = selected_raffle['state_id']
        dsm_enter_raffle.DSM_ZIP_ID = selected_raffle['zip_id']
        dsm_enter_raffle.DSM_MAILING_ID = selected_raffle['mailing_id']
        dsm_enter_raffle.DSM_FORM_ID = selected_raffle['form_id']
        dsm_enter_raffle.DSM_VIEWKEY = selected_raffle['viewkey']
        dsm_enter_raffle.DSM_VIEWPARAM = selected_raffle['viewparam']

        dsm_enter_raffle.DSM_COLOR_ID = selected_raffle['color_id']
        dsm_enter_raffle.DSM_COLOR = selected_raffle['color']

        dsm_enter_raffle.DSM_HIDDEN_FIELDS = selected_raffle['hidden_fields']
        dsm_enter_raffle.DSM_QUESTION_ID = selected_raffle['question_id']

        dsm_enter_raffle.DSM_PLUSTRICK_ENABLED = self.gmail_enabled.value()
        dsm_enter_raffle.DSM_GMAIL = self.gmail_plus_textbox.value()
        dsm_enter_raffle.DSM_CATCHALL_ENABLED = self.catchall_enabled.value()
        dsm_enter_raffle.DSM_CATCHALL = self.catchall_domain.value()
