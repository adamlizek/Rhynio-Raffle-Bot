from PyQt5.QtWidgets import QStackedWidget
from src.ui.components.dynamic_task_settings import naked_settings, naked_new_settings, premier_settings, lapstone_settings, dtlr_settings, b4b_settings, bodega_settings, undefeated_settings, dsm_settings, dsml_settings, sjs_settings, atmos_settings
import src.ui.settings as SETTINGS
import config as CONFIG


class TaskSetupManager(QStackedWidget):
    def __init__(self):
        super(QStackedWidget, self).__init__()
        self.init_pages()
        
    def init_pages(self):
        self.addWidget(atmos_settings.AtmosSettings())
        self.addWidget(b4b_settings.B4BSettings())
        self.addWidget(bodega_settings.BodegaSettings())
        self.addWidget(dsm_settings.DSMSettings())
        self.addWidget(dsml_settings.DSMLSettings())
        self.addWidget(dtlr_settings.DTLRSettings())
        self.addWidget(lapstone_settings.LapstoneSettings())
        self.addWidget(naked_new_settings.NewNakedSettings())
        self.addWidget(premier_settings.PremierSettings())
        self.addWidget(sjs_settings.SJSSettings())
        self.addWidget(undefeated_settings.UndefeatedSettings())

    def refresh(self):
        new_site_index = None

        for key, value in SETTINGS.SITES.items():
            if value == SETTINGS.selected_site:
                new_site_index = key

        self.setCurrentIndex(new_site_index)
        self.currentWidget().refresh()

    def load_task_settings(self):
        self.currentWidget().load_task_settings()
