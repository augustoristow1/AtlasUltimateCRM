"""
Atlas Ultimate CRM - Dark premium theme.
Black/white/grey, clean typography, minimal borders.
"""

COLORS = {
    "bg_primary": "#0f0f0f",
    "bg_secondary": "#1a1a1a",
    "bg_card": "#1e1e1e",
    "bg_hover": "#252525",
    "bg_selected": "#2a2a2a",
    "border": "#2d2d2d",
    "border_light": "#383838",
    "text_primary": "#f0f0f0",
    "text_secondary": "#a0a0a0",
    "text_muted": "#666666",
    "accent": "#3b82f6",
    "accent_hover": "#2563eb",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "white": "#ffffff",
}

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-family: -apple-system, 'SF Pro Display', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}}

QScrollArea {{
    border: none;
    background-color: transparent;
}}

QScrollBar:vertical {{
    background: {COLORS['bg_secondary']};
    width: 6px;
    border-radius: 3px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS['border_light']};
    border-radius: 3px;
    min-height: 30px;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QPushButton {{
    background-color: {COLORS['accent']};
    color: {COLORS['white']};
    border: none;
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 500;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {COLORS['accent_hover']};
}}

QPushButton:pressed {{
    background-color: #1d4ed8;
}}

QPushButton.secondary {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
}}

QPushButton.secondary:hover {{
    background-color: {COLORS['bg_hover']};
}}

QPushButton.danger {{
    background-color: {COLORS['danger']};
}}

QLineEdit, QTextEdit, QComboBox {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 7px 10px;
    font-size: 13px;
}}

QLineEdit:focus, QTextEdit:focus {{
    border: 1px solid {COLORS['accent']};
}}

QComboBox::drop-down {{
    border: none;
    width: 24px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    selection-background-color: {COLORS['bg_selected']};
}}

QTableWidget {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    border: none;
    gridline-color: {COLORS['border']};
    font-size: 13px;
}}

QTableWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid {COLORS['border']};
}}

QTableWidget::item:selected {{
    background-color: {COLORS['bg_selected']};
    color: {COLORS['text_primary']};
}}

QHeaderView::section {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    border: none;
    border-bottom: 1px solid {COLORS['border']};
    padding: 8px 12px;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLabel {{
    color: {COLORS['text_primary']};
    background: transparent;
}}

QLabel.muted {{
    color: {COLORS['text_secondary']};
    font-size: 12px;
}}

QLabel.title {{
    font-size: 22px;
    font-weight: 700;
    color: {COLORS['white']};
}}

QLabel.subtitle {{
    font-size: 14px;
    font-weight: 600;
    color: {COLORS['text_secondary']};
}}

QFrame.card {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 10px;
}}

QFrame.separator {{
    background-color: {COLORS['border']};
    max-height: 1px;
}}

QDialog {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
}}

QMessageBox {{
    background-color: {COLORS['bg_secondary']};
}}

QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    background-color: {COLORS['bg_primary']};
}}

QTabBar::tab {{
    background-color: transparent;
    color: {COLORS['text_secondary']};
    padding: 8px 16px;
    border-bottom: 2px solid transparent;
}}

QTabBar::tab:selected {{
    color: {COLORS['accent']};
    border-bottom: 2px solid {COLORS['accent']};
}}

QTabBar::tab:hover {{
    color: {COLORS['text_primary']};
}}

QSplitter::handle {{
    background-color: {COLORS['border']};
    width: 1px;
}}

QListWidget {{
    background-color: {COLORS['bg_primary']};
    border: none;
    color: {COLORS['text_primary']};
}}

QListWidget::item {{
    padding: 4px 8px;
    border-radius: 4px;
}}

QListWidget::item:selected {{
    background-color: {COLORS['bg_selected']};
}}

QListWidget::item:hover {{
    background-color: {COLORS['bg_hover']};
}}

QCheckBox {{
    color: {COLORS['text_primary']};
    spacing: 8px;
}}

QDateTimeEdit {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 7px 10px;
}}
"""


def get_badge_style(color: str) -> str:
    return f"""
        background-color: {color}22;
        color: {color};
        border: 1px solid {color}44;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 11px;
        font-weight: 600;
    """
