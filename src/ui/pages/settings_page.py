from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import config as CONFIG
from src.ui.components.form.show_failure_checkbox import ShowFailureCheckbox
from src.ui.components.form.captcha_solver_dropdown import CaptchaSolverDropdown
from src.ui.components.form.use_basic_addresses_checkbox import UseBasicAddressesCheckbox
import src.ui.settings as SETTINGS
import json


class SettingsPage(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        self.init_properties()
        self.init_components()
        self.align_components()
        self.apply_to_central_widget()

    def init_properties(self):
        # # apply styling
        with open(str(Path(CONFIG.ROOT, "data/css/main.css")), "r") as stylesheet:
            self.setStyleSheet(stylesheet.read())

        # stylesheet = """
        #     QWidget#content {
        #         background-color: rgb(200, 200, 200);
        #     }

        #     QLabel {
        #         font-size: 18px;
        #         color: black;
        #     }

        #     QLabel#title {
        #         font-size: 24px;
        #         color: black;
        #         margin-bottom: 20px;
        #     }

        #     QPushButton {
        #         background-color: #ec7200;
        #         color: black;
        #         height: 50px; 
        #         font-size: 14px;
        #         font-weight: 700;
        #         border-radius: 100%;
        #     }

        #     QPushButton::hover {
        #         background-color: #eb9443;
        #     }

        #     QMessageBox {
        #         background-color: white;
        #     }

        #     QMessageBox QPushButton {
        #         width: 80px;
        #     }

        #     QMessageBox QLabel {
        #         color: black;
        #     }

        #     QLineEdit {
        #         background-color: white;
        #         color: black;
        #     }
        # """

        # self.setStyleSheet(stylesheet)

    def init_components(self):
        self.central_widget = QWidget()
        self.central_widget.setObjectName("content")

        self.left_column = self.create_left_column()

    def align_components(self):
        layout = QHBoxLayout()

        # 1:3 ratio for left:right column
        layout.addWidget(self.left_column)

        self.central_widget.setLayout(layout)

    def create_left_column(self):
        left_column = QWidget()

        layout = QVBoxLayout()
        left_column.setLayout(layout)

        layout.setAlignment(Qt.AlignTop)

        with open(str(Path(CONFIG.ROOT + '/data/user/saved_info.json'))) as file:
            data = json.load(file)
            CONFIG.two_captcha_api_key = data['TWO_CAPTCHA_API_KEY']
            CONFIG.anticaptcha_api_key = data['ANTI_CAPTCHA_API_KEY']

            try:
                CONFIG.capmonster_api_key = data['CAPMONSTER_API_KEY']
            except KeyError:
                CONFIG.capmonster_api_key = ''

            if data['CAPTCHA_SOLVER'] == 'ANTICAPTCHA':
                CONFIG.CAPTCHA_SOLVER = CONFIG.CaptchaSolver.ANTI_CAPTCHA
            elif data['CAPTCHA_SOLVER'] == 'CAPMONSTER':
                CONFIG.CAPTCHA_SOLVER = CONFIG.CaptchaSolver.CAPMONSTER_CAPTCHA
            else:
                CONFIG.CAPTCHA_SOLVER = CONFIG.CaptchaSolver.TWO_CAPTCHA

            CONFIG.license_key = data['ACCESS_KEY']
            CONFIG.global_webhook = data['WEBHOOK']

            try:
                CONFIG.token = data['TOKEN']
            except KeyError:
                if CONFIG.DEBUG_MODE:
                    print('No Token In JSON')

        title = QLabel("Settings")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignHCenter)
        layout.addWidget(title)

        two_captcha_row = self.create_two_captcha_row()
        layout.addWidget(two_captcha_row)

        anti_captcha_row = self.create_anti_captcha_row()
        layout.addWidget(anti_captcha_row)

        capmonster_row = self.create_capmonster_row()
        layout.addWidget(capmonster_row)

        license_key_row = self.create_license_key_row()
        layout.addWidget(license_key_row)

        global_webhook_row = self.create_global_webhook_row()
        layout.addWidget(global_webhook_row)

        captcha_solver_row = self.create_captcha_solver_row()
        layout.addWidget(captcha_solver_row)

        show_failure_row = self.create_show_failure_row()
        layout.addWidget(show_failure_row)

        use_basic_addresses_row = self.create_use_basic_addresses_row()
        layout.addWidget(use_basic_addresses_row)

        update_settings_btn = QPushButton("Update Settings")
        update_settings_btn.clicked.connect(self.update_settings)
        layout.addWidget(update_settings_btn)

        return left_column

    def create_two_captcha_row(self):
        row = QWidget()
        layout = QHBoxLayout()
        row.setLayout(layout)

        label = QLabel("2Captcha API Key")
        layout.addWidget(label)

        self.two_captcha_api_textbox = QLineEdit()
        self.two_captcha_api_textbox.setText(CONFIG.two_captcha_api_key)
        layout.addWidget(self.two_captcha_api_textbox)

        return row

    def create_anti_captcha_row(self):
        row = QWidget()
        layout = QHBoxLayout()
        row.setLayout(layout)

        label = QLabel("Anti-Captcha API Key")
        layout.addWidget(label)

        self.anti_captcha_api_textbox = QLineEdit()
        self.anti_captcha_api_textbox.setText(CONFIG.anticaptcha_api_key)
        layout.addWidget(self.anti_captcha_api_textbox)

        return row


    def create_capmonster_row(self):
        row = QWidget()
        layout = QHBoxLayout()
        row.setLayout(layout)

        label = QLabel("Capmonster API Key")
        layout.addWidget(label)

        self.capmonster_api_textbox = QLineEdit()
        self.capmonster_api_textbox.setText(CONFIG.capmonster_api_key)
        layout.addWidget(self.capmonster_api_textbox)

        return row

    def create_license_key_row(self):
        row = QWidget()
        layout = QHBoxLayout()
        row.setLayout(layout)

        label = QLabel("License Key")
        layout.addWidget(label)

        self.license_key_textbox = QLineEdit()
        self.license_key_textbox.setText(CONFIG.license_key)
        layout.addWidget(self.license_key_textbox)

        return row

    def create_global_webhook_row(self):
        row = QWidget()
        layout = QHBoxLayout()
        row.setLayout(layout)

        label = QLabel("Global Webhook")
        layout.addWidget(label)

        self.global_webhook_textbox = QLineEdit()
        self.global_webhook_textbox.setText(CONFIG.global_webhook)
        layout.addWidget(self.global_webhook_textbox)

        return row

    def create_captcha_solver_row(self):
        row = QWidget()
        layout = QHBoxLayout()
        row.setLayout(layout)

        label = QLabel("Captcha Solver")
        layout.addWidget(label)

        self.captcha_solver_dropdown = CaptchaSolverDropdown()
        if CONFIG.CAPTCHA_SOLVER == CONFIG.CaptchaSolver.TWO_CAPTCHA:
            self.captcha_solver_dropdown.setIndex(0)
        elif CONFIG.CAPTCHA_SOLVER == CONFIG.CaptchaSolver.ANTI_CAPTCHA:
            self.captcha_solver_dropdown.setIndex(1)
        else:
            self.captcha_solver_dropdown.setIndex(2)

        layout.addWidget(self.captcha_solver_dropdown)

        return row

    def create_show_failure_row(self):
        row = QWidget()
        layout = QHBoxLayout()
        row.setLayout(layout)

        label = QLabel("Show Failures")
        layout.addWidget(label)

        self.show_failure_checkbox = ShowFailureCheckbox()
        layout.addWidget(self.show_failure_checkbox)

        return row

    def create_use_basic_addresses_row(self):
        row = QWidget()
        layout = QHBoxLayout()
        row.setLayout(layout)

        label = QLabel("Use Basic Addresses")
        layout.addWidget(label)

        self.use_basic_addresses = UseBasicAddressesCheckbox()
        layout.addWidget(self.use_basic_addresses)

        return row

    def apply_to_central_widget(self):
        core_layout = QHBoxLayout()
        core_layout.addWidget(self.central_widget)
        core_layout.setContentsMargins(0,0,0,0)
        self.setLayout(core_layout)


    # ===========================
    # ===== SLOTS / ACTIONS =====
    # ===========================
    def update_settings(self):
        CONFIG.two_captcha_api_key = self.two_captcha_api_textbox.text().rstrip()
        CONFIG.anticaptcha_api_key = self.anti_captcha_api_textbox.text().rstrip()
        CONFIG.capmonster_api_key = self.capmonster_api_textbox.text().rstrip()
        CONFIG.license_key = self.license_key_textbox.text().rstrip()
        CONFIG.global_webhook = self.global_webhook_textbox.text().rstrip()
        CONFIG.SHOW_FAILURE = self.show_failure_checkbox.value()
        CONFIG.USE_FAKER = self.use_basic_addresses.value()

        CONFIG.CAPTCHA_SOLVER = self.captcha_solver_dropdown.value()

        if self.captcha_solver_dropdown.value() == 'Anticaptcha':
            CONFIG.CAPTCHA_SOLVER = CONFIG.CaptchaSolver.ANTI_CAPTCHA
            captcha_solver = "ANTICAPTCHA"
        elif self.captcha_solver_dropdown.value() == 'Capmonster':
            CONFIG.CAPTCHA_SOLVER = CONFIG.CaptchaSolver.CAPMONSTER_CAPTCHA
            captcha_solver = "CAPMONSTER"
        else:
            CONFIG.CAPTCHA_SOLVER = CONFIG.CaptchaSolver.TWO_CAPTCHA
            captcha_solver = "2CAPTCHA"

        user_info = {
            "ACCESS_KEY": CONFIG.license_key,
            "TWO_CAPTCHA_API_KEY": CONFIG.two_captcha_api_key,
            "ANTI_CAPTCHA_API_KEY": CONFIG.anticaptcha_api_key,
            "CAPMONSTER_API_KEY": CONFIG.capmonster_api_key,
            "CAPTCHA_SOLVER": captcha_solver,
            "WEBHOOK": CONFIG.global_webhook,
            "TOKEN": CONFIG.token
        }
        with open(str(Path(CONFIG.ROOT + '/data/user/saved_info.json')), 'w') as f:
            json.dump(user_info, f, indent=2)

        QMessageBox.about(self, 'Message', 'Updating Settings!')
