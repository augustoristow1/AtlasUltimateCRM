from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from atlas_ultimate_crm.domain.enums.contact import LifecycleStage
from atlas_ultimate_crm.ui.theme import COLORS


class NewContactDialog(QDialog):
    def __init__(self, bootstrap, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self.setWindowTitle("Novo Contato")
        self.setMinimumWidth(440)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Novo Contato")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {COLORS['white']};")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self._name = QLineEdit()
        self._name.setPlaceholderText("Nome completo")
        self._phone = QLineEdit()
        self._phone.setPlaceholderText("+55 11 99999-9999")
        self._email = QLineEdit()
        self._email.setPlaceholderText("email@exemplo.com")
        self._city = QLineEdit()
        self._job_title = QLineEdit()
        self._lifecycle = QComboBox()
        for stage in LifecycleStage:
            self._lifecycle.addItem(stage.value, stage)

        form.addRow("Nome*:", self._name)
        form.addRow("Telefone:", self._phone)
        form.addRow("Email:", self._email)
        form.addRow("Cidade:", self._city)
        form.addRow("Cargo:", self._job_title)
        form.addRow("Estágio:", self._lifecycle)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setProperty("class", "secondary")
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
        self._bs.contact_service.create_contact(
            workspace_id=self._bs.workspace_id,
            name=name,
            phone=self._phone.text().strip(),
            email=self._email.text().strip(),
            city=self._city.text().strip(),
            job_title=self._job_title.text().strip(),
        )
        self.accept()


class ContactDetailDialog(QDialog):
    def __init__(self, bootstrap, contact_id: str, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self._contact_id = contact_id
        self.setWindowTitle("Contato")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self._contact = bootstrap.contact_service.get_contact(contact_id)
        self._setup_ui()

    def _setup_ui(self):
        if not self._contact:
            layout = QVBoxLayout(self)
            layout.addWidget(QLabel("Contato não encontrado."))
            return

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        c = self._contact
        name_label = QLabel(c.name)
        name_label.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {COLORS['white']};")
        layout.addWidget(name_label)

        info_row = QHBoxLayout()
        for text in [c.phone or "Sem telefone", c.email or "Sem email", c.lifecycle_stage.value]:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; padding: 4px 8px; background: {COLORS['bg_card']}; border-radius: 4px;")
            info_row.addWidget(lbl)
        info_row.addStretch()
        layout.addLayout(info_row)

        tabs = QTabWidget()

        # Timeline tab
        timeline_tab = QWidget()
        tl_layout = QVBoxLayout(timeline_tab)
        activities = self._bs.activity_service.list_for_contact(c.id)
        if activities:
            for act in activities:
                row = QLabel(f"  {act.activity_type.value.replace('_', ' ').title()}  —  {act.created_at.strftime('%d/%m/%Y %H:%M')}")
                row.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; padding: 6px 12px; background: {COLORS['bg_card']}; border-radius: 6px;")
                tl_layout.addWidget(row)
        else:
            tl_layout.addWidget(QLabel("Nenhuma atividade registrada."))
        tl_layout.addStretch()
        tabs.addTab(timeline_tab, "Timeline")

        # Tasks tab
        tasks_tab = QWidget()
        tsk_layout = QVBoxLayout(tasks_tab)
        from sqlalchemy import select

        from atlas_ultimate_crm.infrastructure.database.models.activities import TaskModel
        with self._bs.session_context() as session:
            stmt = select(TaskModel).where(TaskModel.contact_id == c.id).order_by(TaskModel.due_at)
            tasks = session.scalars(stmt).all()
        if tasks:
            for t in tasks:
                row = QLabel(f"  [{t.status}]  {t.title}  —  {t.due_at.strftime('%d/%m/%Y') if t.due_at else 'Sem prazo'}")
                row.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; padding: 6px 12px; background: {COLORS['bg_card']}; border-radius: 6px;")
                tsk_layout.addWidget(row)
        else:
            tsk_layout.addWidget(QLabel("Nenhuma tarefa."))
        tsk_layout.addStretch()
        tabs.addTab(tasks_tab, "Tarefas")

        layout.addWidget(tabs)

        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
