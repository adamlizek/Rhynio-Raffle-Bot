from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QStackedWidget, QGraphicsDropShadowEffect, QPushButton
from src.ui.pages import main_page, task_setup_page, raffles_page, proxies_page, entry_information_page, emails_page, accounts_page, settings_page


class PageManager(QStackedWidget):
    def __init__(self):
        super(QStackedWidget, self).__init__()
        self.setup_pages()

    def setup_pages(self):
        self.addWidget(main_page.MainPage())
        self.addWidget(task_setup_page.TaskSetupPage(self))
        self.addWidget(raffles_page.RafflesPage())
        self.addWidget(proxies_page.ProxiesPage())
        self.addWidget(emails_page.EmailsPage())
        self.addWidget(entry_information_page.EntryInformationPage())
        self.addWidget(accounts_page.AccountsPage())
        self.addWidget(settings_page.SettingsPage())
        
        for children in self.findChildren(QPushButton):
            shadow = QGraphicsDropShadowEffect(blurRadius=5, xOffset=5, yOffset=5, color=QColor(0, 0, 0, 20))
            children.setGraphicsEffect(shadow)
            

    def open_main_page(self):
        self.setCurrentIndex(0)

    def open_task_setup_page(self):
        self.setCurrentIndex(1)

    def open_raffles_page(self):
        self.setCurrentIndex(2)

    def open_proxies_page(self):
        self.setCurrentIndex(3)

    def open_emails_page(self):
        self.setCurrentIndex(4)

    def open_entry_information_page(self):
        self.setCurrentIndex(5)

    def open_accounts_page(self):
        self.setCurrentIndex(6)

    def open_settings_page(self):
        self.setCurrentIndex(7)

    def update_main_page(self):
        self.widget(0).refresh()

