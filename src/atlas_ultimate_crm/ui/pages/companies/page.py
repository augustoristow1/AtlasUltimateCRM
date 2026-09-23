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


class CompaniesPage(QWidget):
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
        title = QLabel("Empresas")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {COLORS['white']};")
        header_row.addWidget(title)
        header_row.addStretch()

        self._search = QLineEdit()
        self._search.setPlaceholderText("Buscar empresas...")
        self._search.setFixedWidth(240)
        self._search.textChanged.connect(lambda t: self.refresh(t))
        header_row.addWidget(self._search)

        new_btn = QPushButton("+ Nova Empresa")
        new_btn.clicked.connect(self._new_company)
        header_row.addWidget(new_btn)
        layout.addLayout(header_row)

        self._count_label = QLabel("")
        self._count_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(self._count_label)

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Nome", "Setor", "Cidade", "Telefone", "Criado em"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

    def refresh(self, search: str = ""):
        companies = self._bs.company_service.list_companies(self._bs.workspace_id, search=search)
        self._count_label.setText(f"{len(companies)} empresas")
        self._table.setRowCount(len(companies))
        for i, c in enumerate(companies):
            self._table.setItem(i, 0, QTableWidgetItem(c.name))
            self._table.setItem(i, 1, QTableWidgetItem(c.industry or "—"))
            self._table.setItem(i, 2, QTableWidgetItem(c.city or "—"))
            self._table.setItem(i, 3, QTableWidgetItem(c.phone or "—"))
            self._table.setItem(i, 4, QTableWidgetItem(c.created_at.strftime("%d/%m/%Y")))
            self._table.setRowHeight(i, 44)

    def _new_company(self):
        from atlas_ultimate_crm.ui.dialogs.company_dialog import NewCompanyDialog
        dlg = NewCompanyDialog(self._bs, self)
        if dlg.exec():
            self.refresh()
