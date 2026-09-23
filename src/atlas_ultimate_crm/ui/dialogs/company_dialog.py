from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from atlas_ultimate_crm.ui.theme import COLORS


class NewCompanyDialog(QDialog):
    def __init__(self, bootstrap, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self.setWindowTitle("Nova Empresa")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Nova Empresa")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLORS['white']};")
        layout.addWidget(title)

        form = QFormLayout()
        self._name = QLineEdit()
        self._name.setPlaceholderText("Nome da empresa")
        self._industry = QLineEdit()
        self._industry.setPlaceholderText("Tecnologia, Saúde...")
        self._city = QLineEdit()
        self._phone = QLineEdit()
        self._email = QLineEdit()
        self._website = QLineEdit()

        form.addRow("Nome*:", self._name)
        form.addRow("Setor:", self._industry)
        form.addRow("Cidade:", self._city)
        form.addRow("Telefone:", self._phone)
        form.addRow("Email:", self._email)
        form.addRow("Website:", self._website)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet(f"background-color: {COLORS['bg_card']}; color: {COLORS['text_primary']}; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 7px 16px;")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Salvar")
        save_btn.clicked.connect(self._save)
        btns.addWidget(cancel_btn)
        btns.addWidget(save_btn)
        layout.addLayout(btns)

    def _save(self):
        name = self._name.text().strip()
        if not name:
            self._name.setStyleSheet(f"border: 1px solid {COLORS['danger']};")
            return
        self._bs.company_service.create_company(
            workspace_id=self._bs.workspace_id,
            name=name,
            industry=self._industry.text().strip(),
            city=self._city.text().strip(),
            phone=self._phone.text().strip(),
            email=self._email.text().strip(),
            website=self._website.text().strip(),
        )
        self.accept()
