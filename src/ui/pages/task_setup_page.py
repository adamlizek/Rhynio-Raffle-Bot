from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import config as CONFIG
import src.ui.settings as SETTINGS
from src.ui.components.managers.task_setup_manager import TaskSetupManager


class TaskSetupPage(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
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

        #     QLabel#dynamic-settings-title {
        #         font-size: 24px;
        #         color: black;
        #         margin-bottom: 20px;
        #     }

        #     QLabel#task-selection-title {
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
        #         border-radius: 5px;
        #     }

        #     QPushButton::hover {
        #         background-color: #eb9443;
        #     }

        #     QComboBox {
        #         color: black;
        #     }

        #     QComboBox QAbstractItemView {
        #         background-color: white;
        #         selection-background-color: #ec7200;
        #     }

        #     QFrame#vertical_line {
        #         color: #191b25;
        #     }

        #     QSpinBox {
        #         background-color: white;
        #         color: black;
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

        #     QWidget#site-row {
        #         margin-top: 20px;
        #     }

        #     QLineEdit {
        #         background-color: white;
        #         color: black;
        #     }
        # """

        # self.setStyleSheet(stylesheet)
    
    def init_components(self):
        self.task_setup_manager = TaskSetupManager()
        
        self.central_widget = QWidget()
        self.central_widget.setObjectName("content")

        self.left_column = self.create_left_column()
        self.vertical_line = self.create_vertical_line()
        self.right_column = self.create_right_column()

    def align_components(self):
        layout = QHBoxLayout()

        # 1:3 ratio for left:right column
        layout.addWidget(self.left_column)
        layout.addWidget(self.vertical_line)
        layout.addWidget(self.right_column)

        self.central_widget.setLayout(layout)

    def apply_to_central_widget(self):
        core_layout = QHBoxLayout()
        core_layout.addWidget(self.central_widget)
        core_layout.setContentsMargins(0,0,0,0)
        self.setLayout(core_layout)

    def create_left_column(self):
        left_column = QWidget()

        layout = QVBoxLayout()
        left_column.setLayout(layout)

        layout.setAlignment(Qt.AlignTop)

        title = QLabel("Task Selection")
        title.setObjectName("task-selection-title")
        title.setAlignment(Qt.AlignHCenter)
        layout.addWidget(title)

        site_row = self.create_site_selection_row()
        layout.addWidget(site_row)

        mode_row = self.create_mode_selection_row()
        layout.addWidget(mode_row)

        load_task_btn = QPushButton("Load Task")
        load_task_btn.clicked.connect(self.load_task)
        load_task_btn.clicked.connect(self.task_setup_manager.load_task_settings)
        layout.addWidget(load_task_btn)

        return left_column

    def create_site_selection_row(self):
        site_row = QWidget()
        site_row.setObjectName("site-row")

        site_row_layout = QHBoxLayout()
        site_row.setLayout(site_row_layout)
        
        site_label = QLabel("Site")
        site_row_layout.addWidget(site_label, 1)

        self.site_combobox = QComboBox()
        site_row_layout.addWidget(self.site_combobox, 2)

        for site in SETTINGS.SITES.values():
            self.site_combobox.addItem(site)

        self.site_combobox.currentIndexChanged.connect(self.update_selected_site)
        self.site_combobox.currentIndexChanged.connect(self.update_mode_combobox)
        self.site_combobox.currentIndexChanged.connect(self.task_setup_manager.refresh)


        return site_row

    def create_mode_selection_row(self):
        mode_row = QWidget()
        mode_row_layout = QHBoxLayout()
        mode_row.setLayout(mode_row_layout)
        
        mode_label = QLabel("Mode")
        mode_row_layout.addWidget(mode_label, 1)

        self.mode_combobox = QComboBox()
        mode_row_layout.addWidget(self.mode_combobox, 2)

        self.mode_combobox.currentIndexChanged.connect(self.update_selected_mode)
        self.mode_combobox.currentIndexChanged.connect(self.task_setup_manager.refresh)

        self.update_mode_combobox()

        return mode_row

    def create_right_column(self):
        right_column = QWidget()

        layout = QVBoxLayout()
        right_column.setLayout(layout)

        layout.setAlignment(Qt.AlignTop)

        title = QLabel("Dynamic Settings")
        title.setObjectName("dynamic-settings-title")
        title.setAlignment(Qt.AlignHCenter)
        layout.addWidget(title)

        layout.addWidget(self.task_setup_manager)

        return right_column

    def create_vertical_line(self):
        line = QFrame()
        line.setObjectName("vertical_line")

        line.setFrameShape(QFrame.VLine)
        line.setLineWidth(3)

        return line

    # ===========================
    # ===== SLOTS / ACTIONS =====
    # ===========================
    def load_task(self):
        self.update_selected_action()
        QMessageBox.about(self, 'Message', 'Loaded Task!')

    def update_selected_action(self):
        SETTINGS.selected_action = SETTINGS.ACTIONS[SETTINGS.selected_site][SETTINGS.selected_mode]

        self.parent().update_main_page()

    def update_mode_combobox(self):
        self.mode_combobox.clear()

        modes = SETTINGS.ACTIONS[self.site_combobox.currentText()]

        # only add necessaary modes
        for key, value in modes.items():
            if value != 'DNE':
                self.mode_combobox.addItem(key)

    def update_selected_site(self):
        SETTINGS.selected_site = self.site_combobox.currentText()

    def update_selected_mode(self):
        SETTINGS.selected_mode = self.mode_combobox.currentText()

