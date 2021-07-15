from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import src.ui.settings as SETTINGS
from src.ui.components.form.raffle_dropdown import RaffleDropdown
from src.ui.components.form.gmail_textbox import GmailTextbox
from src.ui.components.form.plustrick_checkbox import PlustrickCheckbox
from src.ui.components.form.catchall_checkbox import CatchallCheckbox
from src.ui.components.form.catchall_textbox import CatchallTextbox
from src.ui.components.form.country_dropdown import CountryDropdown
from src.actions.dsml import dsml_enter_raffle
from src.utils import populate_raffle_info
import config as CONFIG


class DSMLSettings(QStackedWidget):
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

        raffles = populate_raffle_info.get_active_raffles("DSML")
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

    # https://stackoverflow.com/questions/48399579/python-pyqt-checkbox-to-uncheck-all-other-checkboxes
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
        selected_raffle = populate_raffle_info.get_specific_raffle("DSML", self.raffle_dropdown_enter_raffle.value())

        dsml_enter_raffle.DSML_RAFFLE_URL = selected_raffle['raffle_url']
        dsml_enter_raffle.DSML_FORMSTACK_URL = selected_raffle['formstack_url']
        dsml_enter_raffle.DSML_RAFFLE_NAME = selected_raffle['name'].replace(" ", "_")
        dsml_enter_raffle.DSML_NAME_ID = selected_raffle['name_id']
        dsml_enter_raffle.DSML_PHONE_ID = selected_raffle['phone_id']
        dsml_enter_raffle.DSML_EMAIL_ID = selected_raffle['email_id']
        dsml_enter_raffle.DSML_COLOR_ID = selected_raffle['color_id']
        dsml_enter_raffle.DSML_SIZE_ID = selected_raffle['size_id']
        dsml_enter_raffle.DSML_ADDRESS1_ID = selected_raffle['address1_id']
        dsml_enter_raffle.DSML_COUNTRY_ID = selected_raffle['country_id']
        dsml_enter_raffle.DSML_ZIP_ID = selected_raffle['zip_id']
        dsml_enter_raffle.DSML_FORM_ID = selected_raffle['form_id']
        dsml_enter_raffle.DSML_VIEWKEY = selected_raffle['viewkey']
        dsml_enter_raffle.DSML_VIEWPARAM = selected_raffle['viewparam']
        dsml_enter_raffle.DSML_COLOR_VALUE = selected_raffle['color_value']
        dsml_enter_raffle.DSML_HIDDEN_FIELDS = selected_raffle['hidden_fields']

        dsml_enter_raffle.DSML_COUNTRY_NAME = self.country_dropdown.value()
        dsml_enter_raffle.DSML_PLUSTRICK_ENABLED = self.gmail_enabled.value()
        dsml_enter_raffle.DSML_GMAIL = self.gmail_plus_textbox.value()
        dsml_enter_raffle.DSML_CATCHALL_ENABLED = self.catchall_enabled.value()
        dsml_enter_raffle.DSML_CATCHALL = self.catchall_domain.value()
