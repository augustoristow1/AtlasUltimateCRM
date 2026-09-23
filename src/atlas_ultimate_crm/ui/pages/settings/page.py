from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QGroupBox, QFormLayout, QComboBox, QMessageBox
)
from atlas_ultimate_crm.ui.theme import COLORS
from atlas_ultimate_crm.core.config import AppMode


class SettingsPage(QWidget):
    def __init__(self, bootstrap, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        title = QLabel("Configurações")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {COLORS['white']};")
        layout.addWidget(title)

        # General section
        general_group = QGroupBox("Geral")
        general_group.setStyleSheet(f"QGroupBox {{ color: {COLORS['text_primary']}; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 16px; margin-top: 8px; }} QGroupBox::title {{ color: {COLORS['text_secondary']}; }}")
        general_form = QFormLayout(general_group)
        mode_label = QLabel(f"Modo atual: <b>{self._bs.settings.app_mode.value}</b>")
        mode_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        general_form.addRow("App Mode:", mode_label)
        layout.addWidget(general_group)

        # WhatsApp section
        wa_group = QGroupBox("WhatsApp")
        wa_group.setStyleSheet(general_group.styleSheet())
        wa_form = QFormLayout(wa_group)

        self._waba_id = QLineEdit(self._bs.settings.meta_waba_id or "")
        self._waba_id.setPlaceholderText("WABA ID")
        self._phone_id = QLineEdit(self._bs.settings.meta_phone_number_id or "")
        self._phone_id.setPlaceholderText("Phone Number ID")
        self._api_version = QLineEdit(self._bs.settings.meta_graph_api_version or "v19.0")

        wa_form.addRow("WABA ID:", self._waba_id)
        wa_form.addRow("Phone Number ID:", self._phone_id)
        wa_form.addRow("Graph API Version:", self._api_version)

        test_btn = QPushButton("Testar Conexão")
        test_btn.clicked.connect(self._test_connection)
        wa_form.addRow("", test_btn)
        layout.addWidget(wa_group)

        # Dev section
        dev_group = QGroupBox("Desenvolvimento")
        dev_group.setStyleSheet(general_group.styleSheet())
        dev_layout = QVBoxLayout(dev_group)
        dev_label = QLabel(f"Provider: {self._bs.messaging_service.provider_name()}")
        dev_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px;")
        dev_layout.addWidget(dev_label)
        layout.addWidget(dev_group)

        layout.addStretch()

    def _test_connection(self):
        success = self._bs.messaging_provider.test_connection()
        msg = QMessageBox(self)
        if success:
            msg.setWindowTitle("Conexão OK")
            msg.setText("Conexão estabelecida com sucesso!")
            msg.setIcon(QMessageBox.Icon.Information)
        else:
            msg.setWindowTitle("Falha na Conexão")
            msg.setText("Não foi possível conectar ao provedor de mensagens.")
            msg.setIcon(QMessageBox.Icon.Warning)
        msg.exec()
