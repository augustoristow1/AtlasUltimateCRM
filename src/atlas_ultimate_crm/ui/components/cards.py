from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from atlas_ultimate_crm.ui.theme import COLORS


class MetricCard(QFrame):
    def __init__(self, title: str, value: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setProperty("class", "card")
        self.setMinimumWidth(160)
        self.setMinimumHeight(100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;")

        self.value_label = QLabel(value)
        self.value_label.setStyleSheet(f"color: {COLORS['white']}; font-size: 28px; font-weight: 700;")

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 11px;")
            layout.addWidget(sub)

        layout.addStretch()
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 10px;
            }}
        """)

    def set_value(self, value: str):
        self.value_label.setText(value)
