from PySide6.QtWidgets import QLabel
from atlas_ultimate_crm.ui.theme import COLORS, get_badge_style


class Badge(QLabel):
    def __init__(self, text: str, color: str = COLORS['accent'], parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(get_badge_style(color))

    def set_status(self, status: str):
        self.setText(status)
        color_map = {
            "open": COLORS['success'],
            "closed": COLORS['text_muted'],
            "lead": COLORS['accent'],
            "customer": COLORS['success'],
            "running": COLORS['success'],
            "draft": COLORS['text_muted'],
            "completed": COLORS['accent'],
            "pending": COLORS['warning'],
            "sent": COLORS['accent'],
            "failed": COLORS['danger'],
        }
        color = color_map.get(status.lower(), COLORS['text_secondary'])
        self.setStyleSheet(get_badge_style(color))
