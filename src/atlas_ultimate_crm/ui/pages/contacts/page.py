from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from atlas_ultimate_crm.ui.theme import COLORS


class ContactsPage(QWidget):
    def __init__(self, bootstrap, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        # Header row
        header_row = QHBoxLayout()
        title = QLabel("Contatos")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {COLORS['white']};")
        header_row.addWidget(title)
        header_row.addStretch()

        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar contatos...")
        self._search.setFixedWidth(240)
        self._search.textChanged.connect(self._on_search)
        header_row.addWidget(self._search)

        new_btn = QPushButton("+ Novo Contato")
        new_btn.clicked.connect(self._new_contact)
        header_row.addWidget(new_btn)

        layout.addLayout(header_row)

        # Count label
        self._count_label = QLabel("")
        self._count_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(self._count_label)

        # Table
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(["Nome", "Telefone", "Email", "Empresa", "Estágio", "Criado em"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().setVisible(False)
        self._table.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self._table)

    def refresh(self, search: str = ""):
        ws_id = self._bs.workspace_id
        contacts = self._bs.contact_service.list_contacts(ws_id, search=search, limit=200)
        self._count_label.setText(f"{len(contacts)} contatos")
        self._table.setRowCount(len(contacts))
        for i, c in enumerate(contacts):
            self._table.setItem(i, 0, QTableWidgetItem(c.name))
            self._table.setItem(i, 1, QTableWidgetItem(c.phone or "—"))
            self._table.setItem(i, 2, QTableWidgetItem(c.email or "—"))
            self._table.setItem(i, 3, QTableWidgetItem(""))
            self._table.setItem(i, 4, QTableWidgetItem(c.lifecycle_stage.value))
            self._table.setItem(i, 5, QTableWidgetItem(c.created_at.strftime("%d/%m/%Y")))
            self._table.setRowHeight(i, 44)
            # Store contact id
            self._table.item(i, 0).setData(Qt.ItemDataRole.UserRole, c.id)

    def _on_search(self, text: str):
        self.refresh(search=text)

    def _on_double_click(self, index):
        row = index.row()
        item = self._table.item(row, 0)
        if item:
            contact_id = item.data(Qt.ItemDataRole.UserRole)
            from atlas_ultimate_crm.ui.dialogs.contact_dialog import ContactDetailDialog
            dlg = ContactDetailDialog(self._bs, contact_id, self)
            dlg.exec()
            self.refresh()

    def _new_contact(self):
        from atlas_ultimate_crm.ui.dialogs.contact_dialog import NewContactDialog
        dlg = NewContactDialog(self._bs, self)
        if dlg.exec():
            self.refresh()
