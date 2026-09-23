from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from atlas_ultimate_crm.ui.theme import COLORS


NAV_ITEMS = [
    ("dashboard", "Dashboard", "⬛"),
    ("inbox", "Inbox", "💬"),
    ("contacts", "Contatos", "👤"),
    ("companies", "Empresas", "🏢"),
    ("pipeline", "Pipeline", "📊"),
    ("campaigns", "Campanhas", "📢"),
    ("templates", "Templates", "📋"),
    ("tasks", "Tarefas", "✓"),
]


class NavButton(QPushButton):
    def __init__(self, page_id: str, label: str, icon: str, parent=None):
        super().__init__(f"  {icon}  {label}", parent)
        self.page_id = page_id
        self.setCheckable(True)
        self._update_style(False)
        self.setFixedHeight(40)

    def _update_style(self, active: bool):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLORS['bg_selected']};
                    color: {COLORS['white']};
                    border: none;
                    border-radius: 6px;
                    text-align: left;
                    padding: 0 12px;
                    font-size: 13px;
                    font-weight: 600;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_secondary']};
                    border: none;
                    border-radius: 6px;
                    text-align: left;
                    padding: 0 12px;
                    font-size: 13px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_hover']};
                    color: {COLORS['text_primary']};
                }}
            """)

    def setActive(self, active: bool):
        self._update_style(active)
        self.setChecked(active)


class Sidebar(QWidget):
    page_changed = Signal(str)

    def __init__(self, provider_name: str = "Mock", parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self._buttons: dict[str, NavButton] = {}
        self._current = "dashboard"
        self._setup_ui(provider_name)

    def _setup_ui(self, provider_name: str):
        self.setStyleSheet(f"background-color: {COLORS['bg_secondary']}; border-right: 1px solid {COLORS['border']};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(2)

        # Logo
        logo = QLabel("Atlas\nUltimate CRM")
        logo.setStyleSheet(f"""
            color: {COLORS['white']};
            font-size: 16px;
            font-weight: 800;
            letter-spacing: -0.5px;
            padding: 8px 12px 16px 12px;
        """)
        layout.addWidget(logo)

        # Nav items
        for page_id, label, icon in NAV_ITEMS:
            btn = NavButton(page_id, label, icon)
            btn.clicked.connect(lambda checked, pid=page_id: self._on_nav_click(pid))
            self._buttons[page_id] = btn
            layout.addWidget(btn)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px; margin: 8px 0;")
        layout.addWidget(sep)

        # Settings
        settings_btn = NavButton("settings", "Configurações", "⚙")
        settings_btn.clicked.connect(lambda: self._on_nav_click("settings"))
        self._buttons["settings"] = settings_btn
        layout.addWidget(settings_btn)

        layout.addStretch()

        # Status footer
        mode = "Simulação" if "Mock" in provider_name else "Meta Cloud"
        status = QLabel(f"WhatsApp · {mode}")
        status.setStyleSheet(f"""
            color: {COLORS['text_muted']};
            font-size: 11px;
            padding: 8px 12px;
            border-top: 1px solid {COLORS['border']};
        """)
        layout.addWidget(status)

        # Set default active
        self._buttons["dashboard"].setActive(True)

    def _on_nav_click(self, page_id: str):
        if self._current in self._buttons:
            self._buttons[self._current].setActive(False)
        self._current = page_id
        if page_id in self._buttons:
            self._buttons[page_id].setActive(True)
        self.page_changed.emit(page_id)

    def set_active(self, page_id: str):
        self._on_nav_click(page_id)
