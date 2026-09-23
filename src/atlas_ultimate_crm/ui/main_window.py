import logging
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PySide6.QtCore import Qt
from atlas_ultimate_crm.ui.theme import STYLESHEET
from atlas_ultimate_crm.ui.navigation.sidebar import Sidebar

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, bootstrap):
        super().__init__()
        self._bs = bootstrap
        self._pages: dict = {}
        self.setWindowTitle("Atlas Ultimate CRM")
        self.setMinimumSize(1200, 750)
        self.setStyleSheet(STYLESHEET)
        self._setup_ui()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        provider_name = self._bs.messaging_service.provider_name()
        self._sidebar = Sidebar(provider_name=provider_name)
        self._sidebar.page_changed.connect(self._on_page_change)
        layout.addWidget(self._sidebar)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        self._load_page("dashboard")

    def _get_page(self, page_id: str) -> QWidget:
        if page_id not in self._pages:
            page = self._create_page(page_id)
            self._pages[page_id] = page
            self._stack.addWidget(page)
        return self._pages[page_id]

    def _create_page(self, page_id: str) -> QWidget:
        bs = self._bs
        match page_id:
            case "dashboard":
                from atlas_ultimate_crm.ui.pages.dashboard.page import DashboardPage
                return DashboardPage(bs)
            case "inbox":
                from atlas_ultimate_crm.ui.pages.inbox.page import InboxPage
                return InboxPage(bs)
            case "contacts":
                from atlas_ultimate_crm.ui.pages.contacts.page import ContactsPage
                return ContactsPage(bs)
            case "companies":
                from atlas_ultimate_crm.ui.pages.companies.page import CompaniesPage
                return CompaniesPage(bs)
            case "pipeline":
                from atlas_ultimate_crm.ui.pages.pipeline.page import PipelinePage
                return PipelinePage(bs)
            case "campaigns":
                from atlas_ultimate_crm.ui.pages.campaigns.page import CampaignsPage
                return CampaignsPage(bs)
            case "templates":
                from atlas_ultimate_crm.ui.pages.templates.page import TemplatesPage
                return TemplatesPage(bs)
            case "tasks":
                from atlas_ultimate_crm.ui.pages.tasks.page import TasksPage
                return TasksPage(bs)
            case "settings":
                from atlas_ultimate_crm.ui.pages.settings.page import SettingsPage
                return SettingsPage(bs)
            case _:
                placeholder = QWidget()
                from PySide6.QtWidgets import QLabel, QVBoxLayout
                lbl = QLabel(f"Página '{page_id}' em construção")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                QVBoxLayout(placeholder).addWidget(lbl)
                return placeholder

    def _load_page(self, page_id: str):
        page = self._get_page(page_id)
        self._stack.setCurrentWidget(page)
        # Refresh if page has refresh method
        if hasattr(page, "refresh"):
            try:
                page.refresh()
            except Exception as e:
                logger.warning("Page %s refresh error: %s", page_id, e)

    def _on_page_change(self, page_id: str):
        self._load_page(page_id)
