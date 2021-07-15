from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import config as CONFIG
import json


class ProxiesPage(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        self.init_properties()
        self.init_components()
        self.align_components()
        self.apply_to_central_widget()

    def init_properties(self):
        # apply styling
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

        proxies = ''


        try:
            with open(str(Path(CONFIG.ROOT + '/data/proxies/proxy_lists.json'))) as file:
                data = json.load(file)
                for list in data['proxies']:
                    i = len(data['proxies'][0]['proxies'])
                    for proxy in list['proxies']:
                        if i > 1:
                            proxies += proxy + '\n'
                            i -= 1
                        else:
                            proxies += proxy
        except FileNotFoundError:
            if CONFIG.DEBUG_MODE:
                print('Proxy_lists.json missing')

        title = QLabel("Proxies")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignHCenter)
        layout.addWidget(title)

        # When we add proxy lists, we need to match the proxy_list to the name
        with open(str(Path(CONFIG.ROOT + '/data/proxies/proxy_lists.json')), 'r') as json_file:
            data = json.load(json_file)

        proxy_count = self.create_proxy_count_row(len(data['proxies'][0]['proxies']))
        layout.addWidget(proxy_count)

        proxy_list = self.create_proxy_row(proxies)
        layout.addWidget(proxy_list)

        update_settings_btn = QPushButton("Update Proxies")
        update_settings_btn.clicked.connect(self.update_proxies)
        layout.addWidget(update_settings_btn)

        return left_column

    def create_proxy_row(self, proxies):
        row = QWidget()
        layout = QHBoxLayout()
        row.setLayout(layout)

        self.proxy_textbox = QTextEdit()
        self.proxy_textbox.setText(proxies)
        #self.proxy_textbox.setReadOnly(True)
        layout.addWidget(self.proxy_textbox)

        return row

    def create_proxy_count_row(self, count):
        row = QWidget()
        layout = QHBoxLayout()
        row.setLayout(layout)

        self.proxy_count = QLabel("Proxy Count - " + str(count))
        layout.addWidget(self.proxy_count)

        return row

    def apply_to_central_widget(self):
        core_layout = QHBoxLayout()
        core_layout.addWidget(self.central_widget)
        core_layout.setContentsMargins(0,0,0,0)
        self.setLayout(core_layout)

    # ===========================
    # ===== SLOTS / ACTIONS =====
    # ===========================
    def update_proxies(self):
        proxy_list = self.proxy_textbox.toPlainText().splitlines()

        list_name = "main_list"

        data = {
            "proxies": [
                {
                    "list_name": list_name,
                    "proxies": []
                }
            ]
        }

        for proxy in proxy_list:
            formatted_proxy = proxy.rstrip()
            result_from_parsing = [x.strip() for x in formatted_proxy.split(':')]
            if len(result_from_parsing) != 4 and len(result_from_parsing) != 2:
                continue

            data["proxies"][0]["proxies"].append(formatted_proxy)

        with open(str(Path(CONFIG.ROOT + '/data/proxies/proxy_lists.json')), 'w') as f:
            json.dump(data, f, indent=2)

        # When we add proxy lists, we need to match the proxy_list to the name
        self.update_proxy_count(len(data['proxies'][0]['proxies']))
        self.update_textbox(data["proxies"][0])

        QMessageBox.about(self, 'Message', 'Updating Proxies!')

    def update_textbox(self, data):
        proxies = ''
        i = len(data['proxies'])

        for proxy in data['proxies']:
            if i > 1:
                proxies += proxy + '\n'
                i -= 1
            else:
                proxies += proxy

        self.proxy_textbox.setText(proxies)

    def update_proxy_count(self, updated_count):
        string = "Proxy Count - " + str(updated_count)
        self.proxy_count.setText(string)
