import logging

logger = logging.getLogger(__name__)


class CRMApplication:
    def __init__(self, bootstrap):
        self._bootstrap = bootstrap
        self._window = None

    def run(self):
        from atlas_ultimate_crm.ui.main_window import MainWindow
        self._window = MainWindow(self._bootstrap)
        self._window.show()
        logger.info("Atlas Ultimate CRM UI started")
