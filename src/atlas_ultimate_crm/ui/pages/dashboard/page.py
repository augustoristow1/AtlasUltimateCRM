from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
)
from PySide6.QtCore import Qt
from atlas_ultimate_crm.ui.theme import COLORS
from atlas_ultimate_crm.ui.components.cards import MetricCard


class DashboardPage(QWidget):
    def __init__(self, bootstrap, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        header = QLabel("Dashboard")
        header.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {COLORS['white']};")
        layout.addWidget(header)

        # Metrics grid
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(12)

        self._card_contacts = MetricCard("Contatos", "0")
        self._card_conversations = MetricCard("Conversas Abertas", "0")
        self._card_deals = MetricCard("Oportunidades", "0")
        self._card_pipeline = MetricCard("Pipeline Total", "R$ 0")
        self._card_tasks = MetricCard("Tarefas Pendentes", "0")
        self._card_campaigns = MetricCard("Campanhas Ativas", "0")

        for card in [self._card_contacts, self._card_conversations, self._card_deals,
                     self._card_pipeline, self._card_tasks, self._card_campaigns]:
            metrics_layout.addWidget(card)

        layout.addLayout(metrics_layout)

        # Recent activity section
        activity_label = QLabel("Atividade Recente")
        activity_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {COLORS['text_primary']};")
        layout.addWidget(activity_label)

        self._activity_container = QVBoxLayout()
        self._activity_container.setSpacing(8)

        activity_widget = QWidget()
        activity_widget.setLayout(self._activity_container)
        layout.addWidget(activity_widget)

        layout.addStretch()
        scroll.setWidget(container)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def refresh(self):
        ws_id = self._bs.workspace_id
        try:
            contacts = self._bs.contact_service.count_contacts(ws_id)
            self._card_contacts.set_value(str(contacts))

            convs = self._bs.conversation_service._conv_repo.count_open(ws_id)
            self._card_conversations.set_value(str(convs))

            deals = self._bs.deal_service.count_open(ws_id)
            self._card_deals.set_value(str(deals))

            total_value = self._bs.deal_service.total_pipeline_value(ws_id)
            self._card_pipeline.set_value(f"R$ {total_value:,.0f}")

            tasks = self._bs.task_service.count_pending(ws_id)
            self._card_tasks.set_value(str(tasks))

            active_campaigns = self._bs.campaign_service.count_active(ws_id)
            self._card_campaigns.set_value(str(active_campaigns))

            # Recent activities
            while self._activity_container.count():
                item = self._activity_container.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            from atlas_ultimate_crm.infrastructure.database.models.activities import ActivityModel
            from sqlalchemy import select
            with self._bs.session_context() as session:
                stmt = select(ActivityModel).where(
                    ActivityModel.workspace_id == ws_id
                ).order_by(ActivityModel.created_at.desc()).limit(10)
                activities = session.scalars(stmt).all()

            for act in activities:
                row = QLabel(f"  {act.activity_type.replace('_', ' ').title()}  —  {act.created_at.strftime('%d/%m %H:%M')}")
                row.setStyleSheet(f"""
                    color: {COLORS['text_secondary']};
                    font-size: 12px;
                    padding: 6px 12px;
                    background: {COLORS['bg_card']};
                    border-radius: 6px;
                """)
                self._activity_container.addWidget(row)

            if not activities:
                empty = QLabel("  Nenhuma atividade registrada.")
                empty.setStyleSheet(f"color: {COLORS['text_muted']}; font-size: 13px; padding: 12px;")
                self._activity_container.addWidget(empty)

        except Exception as e:
            import logging
            logging.getLogger(__name__).warning("Dashboard refresh error: %s", e)
