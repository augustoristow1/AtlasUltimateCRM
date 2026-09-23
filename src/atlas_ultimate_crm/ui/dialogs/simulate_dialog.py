from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QComboBox
)
from atlas_ultimate_crm.ui.theme import COLORS


class SimulateInboundDialog(QDialog):
    def __init__(self, bootstrap, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self.setWindowTitle("Simular Mensagem Recebida")
        self.setMinimumWidth(420)
        self._contacts = self._bs.contact_service.list_contacts(self._bs.workspace_id, limit=200)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Simular Mensagem Recebida")
        title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COLORS['white']};")
        layout.addWidget(title)

        form = QFormLayout()

        self._contact_combo = QComboBox()
        self._contact_combo.addItem("— Novo contato (via telefone) —", None)
        for c in self._contacts:
            self._contact_combo.addItem(f"{c.name} ({c.phone or 'sem tel'})", c.id)

        self._phone_edit = QLineEdit()
        self._phone_edit.setPlaceholderText("+5511999999999 (se novo contato)")

        self._message_edit = QLineEdit()
        self._message_edit.setPlaceholderText("Texto da mensagem simulada")
        self._message_edit.setText("Olá, tenho interesse!")

        form.addRow("Contato:", self._contact_combo)
        form.addRow("Telefone:", self._phone_edit)
        form.addRow("Mensagem:", self._message_edit)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(f"background-color: {COLORS['bg_card']}; color: {COLORS['text_primary']}; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 7px 16px;")
        cancel_btn.clicked.connect(self.reject)
        sim_btn = QPushButton("Simular")
        sim_btn.clicked.connect(self._simulate)
        btns.addWidget(cancel_btn)
        btns.addWidget(sim_btn)
        layout.addLayout(btns)

    def _simulate(self):
        body = self._message_edit.text().strip()
        if not body:
            return

        ws_id = self._bs.workspace_id
        contact_id = self._contact_combo.currentData()

        if contact_id:
            contact = self._bs.contact_service.get_contact(contact_id)
            phone = contact.phone if contact else ""
        else:
            phone = self._phone_edit.text().strip()
            if not phone:
                self._phone_edit.setStyleSheet(f"border: 1px solid {COLORS['danger']};")
                return
            contact = self._bs.contact_service.get_or_create_by_phone(ws_id, phone)
            contact_id = contact.id

        import uuid
        self._bs.messaging_service.handle_inbound(
            workspace_id=ws_id,
            contact_id=contact_id,
            phone=phone,
            body=body,
            provider_message_id=f"sim_{uuid.uuid4().hex[:12]}",
        )
        self.accept()
