from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from atlas_ultimate_crm.domain.enums.tasks import TaskPriority
from atlas_ultimate_crm.ui.theme import COLORS


class NewTaskDialog(QDialog):
    def __init__(self, bootstrap, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self.setWindowTitle("Nova Tarefa")
        self.setMinimumWidth(400)
        self._contacts = []
        self._contacts = self._bs.contact_service.list_contacts(self._bs.workspace_id, limit=200)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title_lbl = QLabel("Nova Tarefa")
        title_lbl.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLORS['white']};")
        layout.addWidget(title_lbl)

        form = QFormLayout()
        self._title = QLineEdit()
        self._title.setPlaceholderText("Título da tarefa")

        self._priority = QComboBox()
        for p in TaskPriority:
            self._priority.addItem(p.value, p)

        self._due = QDateTimeEdit(QDateTime.currentDateTime())
        self._due.setDisplayFormat("dd/MM/yyyy HH:mm")
        self._due.setCalendarPopup(True)

        self._contact_combo = QComboBox()
        self._contact_combo.addItem("— Nenhum —", None)
        for c in self._contacts:
            self._contact_combo.addItem(c.name, c.id)

        form.addRow("Título*:", self._title)
        form.addRow("Prioridade:", self._priority)
        form.addRow("Vencimento:", self._due)
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
        title = self._title.text().strip()
        if not title:
            return
        from datetime import UTC, datetime
        due_qdt = self._due.dateTime()
        due_dt = datetime(due_qdt.date().year(), due_qdt.date().month(), due_qdt.date().day(),
                         due_qdt.time().hour(), due_qdt.time().minute(), tzinfo=UTC)
        self._bs.task_service.create_task(
            workspace_id=self._bs.workspace_id,
            title=title,
            contact_id=self._contact_combo.currentData(),
            due_at=due_dt,
            priority=self._priority.currentData(),
        )
        self.accept()
