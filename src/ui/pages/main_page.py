import sys
import os
from pathlib import Path
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.ui.components import logger
from src.multithreading import thread_manager
from src.utils import auth
import config as CONFIG
import src.ui.settings as SETTINGS


class MainPage(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        self.init_properties()
        self.init_components()
        self.align_components()
        self.apply_to_central_widget()
        
        self.refresh()

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

        #     QLabel#log-label {
        #         font-size: 24px;
        #     }

        #     QPushButton {
        #         background-color: #ec7200;
        #         color: black;
        #         height: 50px; 
        #         font-size: 18px;
        #         font-weight: 700;
        #         border-radius: 5px;
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


        #     QSpinBox {
        #         background-color: white;
        #         color: black;
        #     }
        # """

        # self.setStyleSheet(stylesheet)
        

    def init_components(self):
        self.central_widget = QWidget()
        self.central_widget.setObjectName("content")

        self.thread_manager = thread_manager.ThreadManager()
        
        self.create_settings_row()
        self.create_logger_column()

    def align_components(self):
        layout = QVBoxLayout()

        layout.addWidget(self.settings_row)
        layout.addWidget(self.logger_column)
                
        self.central_widget.setLayout(layout)

    def apply_to_central_widget(self):
        core_layout = QHBoxLayout()
        core_layout.addWidget(self.central_widget)
        core_layout.setContentsMargins(0,0,0,0)
        
        self.setLayout(core_layout)

    def create_settings_row(self):
        self.settings_row = QWidget()
        self.settings_row.setObjectName("settings-row")

        layout = QHBoxLayout()
        self.settings_row.setLayout(layout)


        # ==========================================
        # ===== Left Column - Current Settings =====
        # ==========================================
        left_column = QWidget()
        layout.addWidget(left_column)

        left_column_layout = QVBoxLayout()
        left_column.setLayout(left_column_layout)

        # currently selected site
        site_row = QWidget()
        left_column_layout.addWidget(site_row)

        left_column_layout.setAlignment(Qt.AlignLeft)

        site_row_layout = QHBoxLayout()
        site_row.setLayout(site_row_layout)

        site_row_layout.setAlignment(Qt.AlignLeft)

        site_label = QLabel("Site: ")
        site_row_layout.addWidget(site_label)

        self.site = QLabel(SETTINGS.selected_site)
        site_row_layout.addWidget(self.site)

        # currently selected mode
        mode_row = QWidget()
        left_column_layout.addWidget(mode_row)

        mode_row_layout = QHBoxLayout()
        mode_row.setLayout(mode_row_layout)

        mode_row_layout.setAlignment(Qt.AlignLeft)

        mode_label = QLabel("Mode: ")
        mode_row_layout.addWidget(mode_label)

        self.mode = QLabel(SETTINGS.selected_mode)
        mode_row_layout.addWidget(self.mode)

        # desired number of threads
        threads_row = QWidget()
        threads_row_layout = QHBoxLayout()

        threads_row_layout.setAlignment(Qt.AlignLeft)

        threads_label = QLabel("Threads: ")
        threads_row_layout.addWidget(threads_label)

        self.num_threads_spinbox = QSpinBox()
        self.num_threads_spinbox.setValue(1)
        threads_row_layout.addWidget(self.num_threads_spinbox)

        threads_row.setLayout(threads_row_layout)
        
        left_column_layout.addWidget(threads_row)


        # ==================================
        # ===== Right Column - Buttons =====
        # ==================================
        right_column = QWidget()
        layout.addWidget(right_column)

        right_column_layout = QVBoxLayout()
        right_column.setLayout(right_column_layout)

        # start btn
        start_threads_btn = QPushButton("Start")
        start_threads_btn.clicked.connect(self.start_threads)
        right_column_layout.addWidget(start_threads_btn)

        # stop btn
        stop_threads_btn = QPushButton("Stop")
        stop_threads_btn.clicked.connect(self.stop_threads)
        right_column_layout.addWidget(stop_threads_btn)
        
    def create_logger_column(self):
        self.logger_column = QWidget()
        
        layout = QVBoxLayout()
        self.logger_column.setLayout(layout)

        title = QLabel("Log")
        title.setObjectName("log-label")
        layout.addWidget(title)
        layout.setAlignment(title, Qt.AlignHCenter)

        self.logger = logger.Logger()
        layout.addWidget(self.logger)

    def refresh(self):
        self.site.setText(SETTINGS.selected_site)
        self.mode.setText(SETTINGS.selected_mode)


    # ===========================
    # ===== SLOTS / ACTIONS =====
    # ===========================
    def start_threads(self):
        if auth.valid_access_key():
            self.thread_manager.start_threads(SETTINGS.selected_action.run, SETTINGS.selected_action.init, self.num_threads_spinbox.value())
            QMessageBox.about(self, 'Message', 'Starting Threads!')
        else:
            QMessageBox.about(self, 'Error', 'Invalid Auth Token!')

    def stop_threads(self):
        self.thread_manager.stop_threads()
        QMessageBox.about(self, 'Message', 'Stopping Threads!')
