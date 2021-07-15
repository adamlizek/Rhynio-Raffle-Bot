from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import src.ui.settings as SETTINGS
from src.ui.components.form.raffle_dropdown import RaffleDropdown
from src.utils import populate_raffle_info
from src.actions.premier import premier_enter_raffle
from src.ui.components.form.custom_zipcode_checkbox import CustomZipcodeCheckbox
from src.ui.components.form.custom_zipcode_textbox import ZipcodeTextbox

class PremierSettings(QStackedWidget):
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

        layout.addWidget(QLabel("No other settings required!"))

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

        raffles = populate_raffle_info.get_active_raffles("PREMIER")
        if raffles.count() == 0:
            self.raffle_dropdown_enter_raffle.raffle_combobox.addItem("No Open Raffles")
        else:
            for raffle in raffles:
                self.raffle_dropdown_enter_raffle.raffle_combobox.addItem(raffle['name'])

        layout.addWidget(self.raffle_dropdown_enter_raffle)

        # ============================
        # ===== ZIPCODE ENABLED =====
        # ============================

        self.zipcode_enabled = CustomZipcodeCheckbox()
        self.custom_zipcode = ZipcodeTextbox()

        layout.addWidget(self.zipcode_enabled)
        layout.addWidget(self.custom_zipcode)

        return settings

    def refresh(self):
        if SETTINGS.selected_mode == 'ACCOUNT GENERATION':
            self.setCurrentIndex(0)
        elif SETTINGS.selected_mode == 'ENTER RAFFLE':
            self.setCurrentIndex(1)

    def load_task_settings(self):
        if SETTINGS.selected_mode == 'ENTER RAFFLE':
            selected_raffle = populate_raffle_info.get_specific_raffle("PREMIER", self.raffle_dropdown_enter_raffle.value())
            premier_enter_raffle.PREMIER_RAFFLE_NAME = selected_raffle['name'].replace(' ', '_')
            premier_enter_raffle.PREMIER_RAFFLE_ID = selected_raffle['id']
            premier_enter_raffle.PREMIER_LOGIN_CAPTCHA = selected_raffle['login_captcha'] == 'True'

            premier_enter_raffle.PREMIER_CUSTOMZIP_ENABLED = self.zipcode_enabled.value()
            premier_enter_raffle.PREMIER_CUSTOMZIP = self.custom_zipcode.value()