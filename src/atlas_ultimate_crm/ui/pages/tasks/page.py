from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QTabWidget
)
from PySide6.QtCore import Qt
from atlas_ultimate_crm.ui.theme import COLORS
from atlas_ultimate_crm.domain.enums.tasks import TaskStatus


class TasksPage(QWidget):
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
        title = QLabel("Tarefas")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {COLORS['white']};")
        header_row.addWidget(title)
        header_row.addStretch()
        new_btn = QPushButton("+ Nova Tarefa")
        new_btn.clicked.connect(self._new_task)
        header_row.addWidget(new_btn)
        layout.addLayout(header_row)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        self._pending_table = self._make_table()
        self._completed_table = self._make_table()
        self._tabs.addTab(self._pending_table, "Pendentes")
        self._tabs.addTab(self._completed_table, "Concluídas")

    def _make_table(self) -> QTableWidget:
        t = QTableWidget()
        t.setColumnCount(5)
        t.setHorizontalHeaderLabels(["Título", "Prioridade", "Vencimento", "Status", "Ação"])
        t.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        t.verticalHeader().setVisible(False)
        return t

    def refresh(self):
        ws_id = self._bs.workspace_id
        pending = self._bs.task_service.list_tasks(ws_id, status=TaskStatus.PENDING)
        completed = self._bs.task_service.list_tasks(ws_id, status=TaskStatus.COMPLETED)
        self._fill_table(self._pending_table, pending, show_complete_btn=True)
        self._fill_table(self._completed_table, completed, show_complete_btn=False)

    def _fill_table(self, table: QTableWidget, tasks, show_complete_btn: bool):
        table.setRowCount(len(tasks))
        for i, t in enumerate(tasks):
            table.setItem(i, 0, QTableWidgetItem(t.title))
            table.setItem(i, 1, QTableWidgetItem(t.priority.value))
            due = t.due_at.strftime("%d/%m/%Y") if t.due_at else "—"
            table.setItem(i, 2, QTableWidgetItem(due))
            table.setItem(i, 3, QTableWidgetItem(t.status.value))
            if show_complete_btn:
                btn = QPushButton("Concluir")
                btn.setStyleSheet(f"background-color: {COLORS['success']}; color: white; border-radius: 4px; padding: 4px 10px; font-size: 11px;")
                btn.clicked.connect(lambda checked, tid=t.id: self._complete_task(tid))
                table.setCellWidget(i, 4, btn)
            table.setRowHeight(i, 44)

    def _complete_task(self, task_id: str):
        self._bs.task_service.complete_task(task_id)
        self.refresh()

    def _new_task(self):
        from atlas_ultimate_crm.ui.dialogs.task_dialog import NewTaskDialog
        dlg = NewTaskDialog(self._bs, self)
        if dlg.exec():
            self.refresh()
