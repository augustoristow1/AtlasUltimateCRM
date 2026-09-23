from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QMenu
)
from PySide6.QtCore import Qt
from atlas_ultimate_crm.ui.theme import COLORS


class DealCard(QFrame):
    def __init__(self, deal, stages_by_id: dict, on_stage_change, parent=None):
        super().__init__(parent)
        self._deal = deal
        self._stages = stages_by_id
        self._on_stage_change = on_stage_change
        self._setup()

    def _setup(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                margin: 4px 0;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        title = QLabel(self._deal.title)
        title.setStyleSheet(f"color: {COLORS['white']}; font-size: 13px; font-weight: 600;")
        title.setWordWrap(True)

        value = QLabel(f"R$ {self._deal.value:,.2f}")
        value.setStyleSheet(f"color: {COLORS['success']}; font-size: 12px;")

        move_btn = QPushButton("Mover estágio ▾")
        move_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['text_muted']};
                border: none;
                font-size: 11px;
                text-align: left;
                padding: 0;
            }}
            QPushButton:hover {{ color: {COLORS['accent']}; }}
        """)
        move_btn.clicked.connect(self._show_stage_menu)

        layout.addWidget(title)
        layout.addWidget(value)
        layout.addWidget(move_btn)

    def _show_stage_menu(self):
        menu = QMenu(self)
        for stage_id, stage_name in self._stages.items():
            if stage_id != self._deal.stage_id:
                action = menu.addAction(stage_name)
                action.setData(stage_id)
        selected = menu.exec(self.cursor().pos())
        if selected:
            self._on_stage_change(self._deal.id, selected.data())


class PipelinePage(QWidget):
    def __init__(self, bootstrap, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 16)
        layout.setSpacing(16)

        header_row = QHBoxLayout()
        title = QLabel("Pipeline")
        title.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {COLORS['white']};")
        header_row.addWidget(title)
        header_row.addStretch()

        new_btn = QPushButton("+ Novo Negócio")
        new_btn.clicked.connect(self._new_deal)
        header_row.addWidget(new_btn)
        layout.addLayout(header_row)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self._scroll)

    def refresh(self):
        ws_id = self._bs.workspace_id
        pipeline, stages = self._bs.pipeline_service.get_or_create_default_pipeline(ws_id)
        deals = self._bs.deal_service.list_deals(ws_id)

        stages_by_id = {s.id: s.name for s in stages}
        deals_by_stage: dict = {s.id: [] for s in stages}
        for deal in deals:
            if deal.stage_id in deals_by_stage:
                deals_by_stage[deal.stage_id].append(deal)

        container = QWidget()
        container.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        cols_layout = QHBoxLayout(container)
        cols_layout.setContentsMargins(0, 0, 0, 0)
        cols_layout.setSpacing(12)
        cols_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        for stage in stages:
            col = self._build_column(stage, deals_by_stage[stage.id], stages_by_id)
            cols_layout.addWidget(col)

        cols_layout.addStretch()
        self._scroll.setWidget(container)

    def _build_column(self, stage, deals: list, stages_by_id: dict) -> QWidget:
        col = QWidget()
        col.setFixedWidth(220)
        col.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 8px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        layout = QVBoxLayout(col)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        header = QLabel(f"{stage.name}  {len(deals)}")
        header.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 700; text-transform: uppercase; padding: 4px 4px 8px 4px;")
        layout.addWidget(header)

        for deal in deals:
            card = DealCard(deal, stages_by_id, self._on_stage_change, col)
            layout.addWidget(card)

        layout.addStretch()
        return col

    def _on_stage_change(self, deal_id: str, new_stage_id: str):
        self._bs.deal_service.change_stage(deal_id, new_stage_id)
        self.refresh()

    def _new_deal(self):
        from atlas_ultimate_crm.ui.dialogs.deal_dialog import NewDealDialog
        dlg = NewDealDialog(self._bs, self)
        if dlg.exec():
            self.refresh()
