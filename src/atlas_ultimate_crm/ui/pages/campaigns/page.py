from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from atlas_ultimate_crm.ui.theme import COLORS


class CampaignsPage(QWidget):
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
        title = QLabel("Campanhas")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {COLORS['white']};")
        header_row.addWidget(title)
        header_row.addStretch()
        new_btn = QPushButton("+ Nova Campanha")
        new_btn.clicked.connect(self._new_campaign)
        header_row.addWidget(new_btn)
        layout.addLayout(header_row)

        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(["Nome", "Status", "Destinatários", "Enviadas", "Respondidas", "Criada em"])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self._table)

    def refresh(self):
        campaigns = self._bs.campaign_service.list_campaigns(self._bs.workspace_id)
        self._table.setRowCount(len(campaigns))
        for i, c in enumerate(campaigns):
            recipients = self._bs.campaign_service._repo.get_recipients(c.id)
            sent = sum(1 for r in recipients if r.status.value in ("sent", "delivered", "read", "replied"))
            replied = sum(1 for r in recipients if r.status.value == "replied")
            self._table.setItem(i, 0, QTableWidgetItem(c.name))
            self._table.setItem(i, 1, QTableWidgetItem(c.status.value))
            self._table.setItem(i, 2, QTableWidgetItem(str(len(recipients))))
            self._table.setItem(i, 3, QTableWidgetItem(str(sent)))
            self._table.setItem(i, 4, QTableWidgetItem(str(replied)))
            self._table.setItem(i, 5, QTableWidgetItem(c.created_at.strftime("%d/%m/%Y")))
            self._table.setRowHeight(i, 44)
            self._table.item(i, 0).setData(Qt.ItemDataRole.UserRole, c.id)

    def _on_double_click(self, index):
        row = index.row()
        item = self._table.item(row, 0)
        if item:
            campaign_id = item.data(Qt.ItemDataRole.UserRole)
            from atlas_ultimate_crm.ui.dialogs.campaign_dialog import CampaignDetailDialog
            dlg = CampaignDetailDialog(self._bs, campaign_id, self)
            dlg.exec()
            self.refresh()

    def _new_campaign(self):
        from atlas_ultimate_crm.ui.dialogs.campaign_dialog import NewCampaignDialog
        dlg = NewCampaignDialog(self._bs, self)
        if dlg.exec():
            self.refresh()
