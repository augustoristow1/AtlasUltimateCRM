from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from atlas_ultimate_crm.ui.theme import COLORS


class EmptyState(QWidget):
    def __init__(self, icon: str, title: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"font-size: 48px; color: {COLORS['text_muted']};")

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {COLORS['text_secondary']};")

        layout.addWidget(icon_label)
        layout.addWidget(title_label)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub.setStyleSheet(f"font-size: 13px; color: {COLORS['text_muted']};")
            layout.addWidget(sub)
