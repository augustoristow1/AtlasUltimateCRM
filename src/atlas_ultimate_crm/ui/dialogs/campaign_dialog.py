from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QComboBox, QListWidget, QListWidgetItem,
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from atlas_ultimate_crm.ui.theme import COLORS


class NewCampaignDialog(QDialog):
    def __init__(self, bootstrap, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self.setWindowTitle("Nova Campanha")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Nova Campanha")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLORS['white']};")
        layout.addWidget(title)

        form = QFormLayout()
        self._name = QLineEdit()
        self._name.setPlaceholderText("Nome da campanha")

        self._template_combo = QComboBox()
        self._template_combo.addItem("— Sem template (texto simples) —", None)
        templates = self._bs.messaging_service.get_templates()
        for t in templates:
            self._template_combo.addItem(f"{t.name} ({t.language})", t.external_id)

        form.addRow("Nome*:", self._name)
        form.addRow("Template:", self._template_combo)
        layout.addLayout(form)

        # Contact selection
        contacts_label = QLabel("Selecionar destinatários:")
        contacts_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 600;")
        layout.addWidget(contacts_label)

        self._contacts_list = QListWidget()
        self._contacts_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        contacts = self._bs.contact_service.list_contacts(self._bs.workspace_id, limit=200)
        for c in contacts:
            item = QListWidgetItem(f"{c.name} — {c.phone or 'sem telefone'}")
            item.setData(Qt.ItemDataRole.UserRole, c.id)
            self._contacts_list.addItem(item)
        layout.addWidget(self._contacts_list)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(f"background-color: {COLORS['bg_card']}; color: {COLORS['text_primary']}; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 7px 16px;")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Criar e Enviar")
        save_btn.clicked.connect(self._save)
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)

    def _save(self):
        name = self._name.text().strip()
        if not name:
            return
        selected = self._contacts_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Atenção", "Selecione pelo menos um destinatário.")
            return
        contact_ids = [item.data(Qt.ItemDataRole.UserRole) for item in selected]
        campaign = self._bs.campaign_service.create_campaign(
            workspace_id=self._bs.workspace_id,
            name=name,
        )
        self._bs.campaign_service.add_recipients(campaign.id, contact_ids)
        self._bs.campaign_service.run_campaign(campaign.id, self._bs.workspace_id)
        self.accept()


class CampaignDetailDialog(QDialog):
    def __init__(self, bootstrap, campaign_id: str, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self._campaign_id = campaign_id
        self.setWindowTitle("Detalhes da Campanha")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        campaign = self._bs.campaign_service._repo.get_by_id(self._campaign_id)
        if not campaign:
            layout.addWidget(QLabel("Campanha não encontrada."))
            return

        title = QLabel(campaign.name)
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLORS['white']};")
        layout.addWidget(title)

        status_label = QLabel(f"Status: {campaign.status.value}")
        status_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(status_label)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Contato", "Status", "Enviado em", "Respondeu em"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setVisible(False)

        recipients = self._bs.campaign_service._repo.get_recipients(self._campaign_id)
        table.setRowCount(len(recipients))
        for i, r in enumerate(recipients):
            contact = self._bs.contact_service.get_contact(r.contact_id)
            name = contact.name if contact else r.contact_id
            table.setItem(i, 0, QTableWidgetItem(name))
            table.setItem(i, 1, QTableWidgetItem(r.status.value))
            table.setItem(i, 2, QTableWidgetItem(r.sent_at.strftime("%d/%m %H:%M") if r.sent_at else "—"))
            table.setItem(i, 3, QTableWidgetItem(r.replied_at.strftime("%d/%m %H:%M") if r.replied_at else "—"))
            table.setRowHeight(i, 40)
        layout.addWidget(table)

        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
