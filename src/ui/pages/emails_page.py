from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import config as CONFIG
from src.ui.components.frameless_messagebox import FramelessMessageBox
import json


class EmailsPage(QWidget):
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

        emails = ''
        try:
            with open(str(Path(CONFIG.ROOT + '/data/emails/emails.json'))) as file:
                data = json.load(file)
                i = len(data['emails'])

                for email in data['emails']:
                    if i > 1:
                        emails += email + '\n'
                        i -= 1

                    else:
                        emails += email
        except FileNotFoundError:
            if CONFIG.DEBUG_MODE:
                print('emails.json missing')

        title = QLabel("Emails")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignHCenter)
        layout.addWidget(title)

        with open(str(Path(CONFIG.ROOT + '/data/emails/emails.json')), 'r') as json_file:
            data = json.load(json_file)

        email_count = self.create_email_count_row(len(data['emails']))
        layout.addWidget(email_count)

        email_list = self.create_email_row(emails)
        layout.addWidget(email_list)

        update_settings_btn = QPushButton("Update Emails")
        update_settings_btn.clicked.connect(self.update_emails)
        layout.addWidget(update_settings_btn)

        return left_column

    def create_email_row(self, emails):
        row = QWidget()
        layout = QHBoxLayout()
        row.setLayout(layout)

        self.email_textbox = QTextEdit()
        self.email_textbox.setText(emails)
        #self.proxy_textbox.setReadOnly(True)
        layout.addWidget(self.email_textbox)

        return row

    def create_email_count_row(self, count):
        row = QWidget()
        layout = QHBoxLayout()
        row.setLayout(layout)

        self.email_count = QLabel("Email Count - " + str(count))
        layout.addWidget(self.email_count)

        return row

    def apply_to_central_widget(self):
        core_layout = QHBoxLayout()
        core_layout.addWidget(self.central_widget)
        core_layout.setContentsMargins(0,0,0,0)
        self.setLayout(core_layout)

    # ===========================
    # ===== SLOTS / ACTIONS =====
    # ===========================
    def update_emails(self):
        emails = self.email_textbox.toPlainText().splitlines()

        data = {
            "emails": []
        }

        for email in emails:
            formatted_email = email.rstrip()
            if '@' in formatted_email:
                data["emails"].append(formatted_email)

        with open(str(Path(CONFIG.ROOT + '/data/emails/emails.json')), 'w') as f:
            json.dump(data, f, indent=2)
        self.update_email_count(len(data['emails']))
        self.update_textbox(data)

        QMessageBox.about(self, 'Message', 'Updated Emails!')
        # FramelessMessageBox('Updated Emails!')   

    def update_textbox(self, data):
        emails = ''
        i = len(data['emails'])

        for email in data['emails']:
            if i > 1:
                emails += email + '\n'
                i -= 1
            else:
                emails += email

        self.email_textbox.setText(emails)

    def update_email_count(self, updated_count):
        string = "Email Count - " + str(updated_count)
        self.email_count.setText(string)
