from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from atlas_ultimate_crm.ui.theme import COLORS


class TemplatesPage(QWidget):
    def __init__(self, bootstrap, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        header_row = QHBoxLayout()
        title = QLabel("Templates")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {COLORS['white']};")
        header_row.addWidget(title)
        header_row.addStretch()
        sync_btn = QPushButton("Sincronizar")
        sync_btn.clicked.connect(self.refresh)
        header_row.addWidget(sync_btn)
        layout.addLayout(header_row)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Nome", "Idioma", "Categoria", "Status"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

    def refresh(self):
        templates = self._bs.messaging_service.get_templates()
        self._table.setRowCount(len(templates))
        for i, t in enumerate(templates):
            self._table.setItem(i, 0, QTableWidgetItem(t.name))
            self._table.setItem(i, 1, QTableWidgetItem(t.language))
            self._table.setItem(i, 2, QTableWidgetItem(t.category))
            self._table.setItem(i, 3, QTableWidgetItem(t.status))
            self._table.setRowHeight(i, 44)
