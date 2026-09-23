from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from atlas_ultimate_crm.ui.theme import COLORS


class NewDealDialog(QDialog):
    def __init__(self, bootstrap, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self.setWindowTitle("Novo Negócio")
        self.setMinimumWidth(420)
        self._pipeline = None
        self._stages = []
        self._contacts = []
        self._load_data()
        self._setup_ui()

    def _load_data(self):
        ws_id = self._bs.workspace_id
        self._pipeline, self._stages = self._bs.pipeline_service.get_or_create_default_pipeline(ws_id)
        self._contacts = self._bs.contact_service.list_contacts(ws_id, limit=200)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Novo Negócio")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLORS['white']};")
        layout.addWidget(title)

        form = QFormLayout()
        self._title_edit = QLineEdit()
        self._title_edit.setPlaceholderText("Título do negócio")

        self._stage_combo = QComboBox()
        for s in self._stages:
            self._stage_combo.addItem(s.name, s.id)

        self._value_spin = QDoubleSpinBox()
        self._value_spin.setMaximum(9_999_999)
        self._value_spin.setPrefix("R$ ")
        self._value_spin.setDecimals(2)

        self._contact_combo = QComboBox()
        self._contact_combo.addItem("— Nenhum —", None)
        for c in self._contacts:
            self._contact_combo.addItem(c.name, c.id)

        form.addRow("Título*:", self._title_edit)
        form.addRow("Estágio:", self._stage_combo)
        form.addRow("Valor:", self._value_spin)
        form.addRow("Contato:", self._contact_combo)
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
        title = self._title_edit.text().strip()
        if not title:
            return
        stage_id = self._stage_combo.currentData()
        contact_id = self._contact_combo.currentData()
        value = self._value_spin.value()
        self._bs.deal_service.create_deal(
            workspace_id=self._bs.workspace_id,
            pipeline_id=self._pipeline.id,
            stage_id=stage_id,
            title=title,
            contact_id=contact_id,
            value=value,
        )
        self.accept()
