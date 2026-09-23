from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from atlas_ultimate_crm.ui.theme import COLORS

_REFRESH_INTERVAL_MS = 5000  # 5 seconds


class ConversationListItem(QListWidgetItem):
    def __init__(self, conversation, contact_name: str, last_message: str):
        super().__init__()
        self.conversation = conversation
        self.contact_name = contact_name
        self.setText(f"{contact_name}\n{last_message[:60] if last_message else 'Sem mensagens'}")
        if conversation.unread_count > 0:
            self.setForeground(Qt.GlobalColor.white)


class InboxPage(QWidget):
    def __init__(self, bootstrap, parent=None):
        super().__init__(parent)
        self._bs = bootstrap
        self._current_conv = None
        self._setup_ui()
        self.refresh()
        self._start_auto_refresh()

    def _start_auto_refresh(self):
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(_REFRESH_INTERVAL_MS)
        self._refresh_timer.timeout.connect(self._auto_refresh)
        self._refresh_timer.start()

    def _auto_refresh(self):
        """Periodic refresh: update conversation list and messages without blocking the UI."""
        selected_conv_id = self._current_conv.id if self._current_conv else None
        self._reload_conv_list(selected_conv_id)
        if self._current_conv:
            self._reload_messages_preserving_scroll()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # Left: conversation list
        left_panel = QWidget()
        left_panel.setFixedWidth(280)
        left_panel.setStyleSheet(f"background-color: {COLORS['bg_secondary']}; border-right: 1px solid {COLORS['border']};")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        inbox_header = QLabel("  Inbox")
        inbox_header.setStyleSheet(f"color: {COLORS['white']}; font-size: 16px; font-weight: 700; padding: 20px 16px 16px 16px; border-bottom: 1px solid {COLORS['border']};")
        left_layout.addWidget(inbox_header)

        self._conv_list = QListWidget()
        self._conv_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['bg_secondary']};
                border: none;
                color: {COLORS['text_primary']};
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 12px 16px;
                border-bottom: 1px solid {COLORS['border']};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS['bg_selected']};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['bg_hover']};
            }}
        """)
        self._conv_list.currentItemChanged.connect(self._on_conv_selected)
        left_layout.addWidget(self._conv_list)

        # Simulate inbound button
        sim_btn = QPushButton("⬇  Simular mensagem recebida")
        sim_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['bg_card']};
                color: {COLORS['text_secondary']};
                border-top: 1px solid {COLORS['border']};
                border-radius: 0;
                padding: 12px;
                font-size: 12px;
                text-align: left;
            }}
            QPushButton:hover {{ color: {COLORS['accent']}; background-color: {COLORS['bg_hover']}; }}
        """)
        sim_btn.clicked.connect(self._simulate_inbound)
        left_layout.addWidget(sim_btn)

        splitter.addWidget(left_panel)

        # Center: chat view
        self._chat_panel = QWidget()
        self._chat_panel.setStyleSheet(f"background-color: {COLORS['bg_primary']};")
        chat_layout = QVBoxLayout(self._chat_panel)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        # Chat header
        self._chat_header = QLabel("  Selecione uma conversa")
        self._chat_header.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 15px; font-weight: 600; padding: 16px; border-bottom: 1px solid {COLORS['border']};")
        chat_layout.addWidget(self._chat_header)

        # Messages area
        self._messages_scroll = QScrollArea()
        self._messages_scroll.setWidgetResizable(True)
        self._messages_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._messages_container = QWidget()
        self._messages_layout = QVBoxLayout(self._messages_container)
        self._messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._messages_layout.setSpacing(8)
        self._messages_layout.setContentsMargins(16, 16, 16, 16)
        self._messages_scroll.setWidget(self._messages_container)
        chat_layout.addWidget(self._messages_scroll)

        # Input area
        input_area = QWidget()
        input_area.setStyleSheet(f"background-color: {COLORS['bg_secondary']}; border-top: 1px solid {COLORS['border']};")
        input_layout = QHBoxLayout(input_area)
        input_layout.setContentsMargins(16, 12, 16, 12)
        input_layout.setSpacing(8)

        self._msg_input = QLineEdit()
        self._msg_input.setPlaceholderText("Digite uma mensagem...")
        self._msg_input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self._msg_input)

        send_btn = QPushButton("Enviar")
        send_btn.setFixedWidth(80)
        send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(send_btn)

        chat_layout.addWidget(input_area)
        splitter.addWidget(self._chat_panel)
        splitter.setSizes([280, 700])

        main_layout.addWidget(splitter)

    def _reload_conv_list(self, selected_conv_id: str | None):
        """Repopulate conversation list, restoring previous selection."""
        # Temporarily block signals to avoid triggering _on_conv_selected during repopulation
        self._conv_list.blockSignals(True)
        self._conv_list.clear()
        convs = self._bs.conversation_service.list_open_conversations(self._bs.workspace_id)
        item_to_select = None
        for conv in convs:
            contact = self._bs.contact_service.get_contact(conv.contact_id)
            name = contact.name if contact else conv.contact_id
            messages = self._bs.conversation_service.list_messages(conv.id, limit=1)
            last_msg = messages[-1].body if messages else ""
            item = ConversationListItem(conv, name, last_msg)
            self._conv_list.addItem(item)
            if selected_conv_id and conv.id == selected_conv_id:
                item_to_select = item
        self._conv_list.blockSignals(False)
        if item_to_select:
            self._conv_list.setCurrentItem(item_to_select)

    def refresh(self):
        selected_conv_id = self._current_conv.id if self._current_conv else None
        self._reload_conv_list(selected_conv_id)

    def _reload_messages_preserving_scroll(self):
        """Reload messages in the chat view, scrolling to bottom only if already at bottom."""
        if not self._current_conv:
            return

        scrollbar = self._messages_scroll.verticalScrollBar()
        at_bottom = scrollbar.value() >= scrollbar.maximum() - 10

        messages = self._bs.conversation_service.list_messages(self._current_conv.id)
        current_count = self._messages_layout.count()

        # Only redraw if message count changed
        if len(messages) == current_count:
            return

        while self._messages_layout.count():
            child = self._messages_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        for msg in messages:
            bubble = self._make_bubble(msg)
            self._messages_layout.addWidget(bubble)

        if at_bottom:
            QTimer.singleShot(50, lambda: self._messages_scroll.verticalScrollBar().setValue(
                self._messages_scroll.verticalScrollBar().maximum()
            ))

    def _on_conv_selected(self, item):
        if not item or not isinstance(item, ConversationListItem):
            return
        self._current_conv = item.conversation
        self._chat_header.setText(f"  {item.contact_name}")
        self._bs.conversation_service.mark_read(item.conversation.id)
        self._load_messages()

    def _load_messages(self):
        if not self._current_conv:
            return
        # Clear
        while self._messages_layout.count():
            child = self._messages_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        messages = self._bs.conversation_service.list_messages(self._current_conv.id)
        for msg in messages:
            bubble = self._make_bubble(msg)
            self._messages_layout.addWidget(bubble)

        # Scroll to bottom
        QTimer.singleShot(50, lambda: self._messages_scroll.verticalScrollBar().setValue(
            self._messages_scroll.verticalScrollBar().maximum()
        ))

    def _make_bubble(self, msg) -> QWidget:
        from atlas_ultimate_crm.domain.enums.messaging import MessageDirection
        is_outbound = msg.direction == MessageDirection.OUTBOUND

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        bubble = QLabel(msg.body or "[mensagem sem texto]")
        bubble.setWordWrap(True)
        bubble.setMaximumWidth(500)
        bubble.setStyleSheet(f"""
            QLabel {{
                background-color: {'#1d4ed8' if is_outbound else COLORS['bg_card']};
                color: {COLORS['white']};
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 13px;
            }}
        """)

        if is_outbound:
            layout.addStretch()
            layout.addWidget(bubble)
        else:
            layout.addWidget(bubble)
            layout.addStretch()

        return container

    def _send_message(self):
        if not self._current_conv:
            return
        text = self._msg_input.text().strip()
        if not text:
            return
        ws_id = self._bs.workspace_id
        contact = self._bs.contact_service.get_contact(self._current_conv.contact_id)
        phone = contact.phone if contact else ""
        self._bs.messaging_service.send_text_to_contact(ws_id, self._current_conv.contact_id, phone, text)
        self._msg_input.clear()
        self._load_messages()

    def _simulate_inbound(self):
        from atlas_ultimate_crm.ui.dialogs.simulate_dialog import SimulateInboundDialog
        dlg = SimulateInboundDialog(self._bs, self)
        if dlg.exec():
            self.refresh()
            if self._current_conv:
                self._load_messages()
