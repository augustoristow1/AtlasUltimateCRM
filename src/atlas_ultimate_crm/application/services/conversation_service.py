import logging
from datetime import UTC, datetime, timedelta
from typing import Sequence

from sqlalchemy import select

from atlas_ultimate_crm.application.event_bus import InMemoryEventBus
from atlas_ultimate_crm.application.services.activity_service import ActivityService
from atlas_ultimate_crm.core.constants import WHATSAPP_SERVICE_WINDOW_HOURS
from atlas_ultimate_crm.domain.entities.conversation import ConversationEntity
from atlas_ultimate_crm.domain.entities.message import MessageEntity
from atlas_ultimate_crm.domain.enums.activities import ActivityType
from atlas_ultimate_crm.domain.enums.messaging import (
    ChannelType,
    MessageDirection,
    MessageStatus,
)
from atlas_ultimate_crm.infrastructure.database.models.conversations import MessageModel

logger = logging.getLogger(__name__)


class ConversationService:
    def __init__(self, event_bus: InMemoryEventBus, session_factory,
                 activity_service: ActivityService) -> None:
        self._event_bus = event_bus
        self._session_factory = session_factory
        self._activity_service = activity_service

    def _repo(self, session):
        from atlas_ultimate_crm.infrastructure.database.repositories.conversation_repository import (
            SQLConversationRepository,
        )
        return SQLConversationRepository(session)

    def get_or_create_conversation(self, workspace_id: str, contact_id: str,
                                   channel: ChannelType = ChannelType.WHATSAPP) -> ConversationEntity:
        with self._session_factory() as session:
            existing = self._repo(session).get_by_contact(workspace_id, contact_id)
            if existing:
                return existing
            conv = ConversationEntity(workspace_id=workspace_id, contact_id=contact_id, channel=channel)
            saved = self._repo(session).save(conv)
            session.commit()
            return saved

    def save_inbound_message(self, workspace_id: str, conversation_id: str, contact_id: str,
                              body: str, provider_message_id: str = "") -> MessageEntity:
        # Idempotency: skip if this provider_message_id was already stored
        if provider_message_id:
            with self._session_factory() as session:
                existing = session.scalars(
                    select(MessageModel).where(
                        MessageModel.provider_message_id == provider_message_id,
                        MessageModel.direction == MessageDirection.INBOUND.value,
                    )
                ).first()
                if existing is not None:
                    logger.debug("Duplicate inbound message ignored: %s", provider_message_id)
                    from atlas_ultimate_crm.domain.enums.messaging import MessageType
                    return MessageEntity(
                        id=existing.id, workspace_id=existing.workspace_id,
                        conversation_id=existing.conversation_id,
                        contact_id=existing.contact_id,
                        provider_message_id=existing.provider_message_id,
                        direction=MessageDirection(existing.direction),
                        message_type=MessageType(existing.message_type),
                        body=existing.body, status=MessageStatus(existing.status),
                        received_at=existing.received_at, created_at=existing.created_at,
                    )

        msg = MessageEntity(
            workspace_id=workspace_id, conversation_id=conversation_id,
            contact_id=contact_id, direction=MessageDirection.INBOUND,
            body=body, provider_message_id=provider_message_id,
            status=MessageStatus.DELIVERED, received_at=datetime.now(UTC),
        )
        with self._session_factory() as session:
            m = MessageModel(
                id=msg.id, workspace_id=msg.workspace_id, conversation_id=msg.conversation_id,
                contact_id=msg.contact_id, provider_message_id=msg.provider_message_id,
                direction=msg.direction.value, message_type=msg.message_type.value,
                body=msg.body, status=msg.status.value, received_at=msg.received_at,
                created_at=msg.created_at,
            )
            session.add(m)
            # Update conversation
            from atlas_ultimate_crm.infrastructure.database.models.conversations import (
                ConversationModel,
            )
            conv_m = session.get(ConversationModel, conversation_id)
            if conv_m:
                now = datetime.now(UTC)
                conv_m.last_message_at = now
                conv_m.last_inbound_at = now
                conv_m.service_window_expires_at = now + timedelta(hours=WHATSAPP_SERVICE_WINDOW_HOURS)
                conv_m.unread_count = (conv_m.unread_count or 0) + 1
            session.commit()
        self._activity_service.record(workspace_id, ActivityType.MESSAGE_RECEIVED, contact_id=contact_id)
        return msg

    def save_outbound_message(self, workspace_id: str, conversation_id: str, contact_id: str,
                               body: str, provider_message_id: str = "") -> MessageEntity:
        msg = MessageEntity(
            workspace_id=workspace_id, conversation_id=conversation_id,
            contact_id=contact_id, direction=MessageDirection.OUTBOUND,
            body=body, provider_message_id=provider_message_id,
            status=MessageStatus.SENT, sent_at=datetime.now(UTC),
        )
        with self._session_factory() as session:
            from atlas_ultimate_crm.infrastructure.database.models.conversations import (
                ConversationModel,
            )
            from atlas_ultimate_crm.infrastructure.database.models.conversations import (
                MessageModel as MM,
            )
            m = MM(
                id=msg.id, workspace_id=msg.workspace_id, conversation_id=msg.conversation_id,
                contact_id=msg.contact_id, provider_message_id=msg.provider_message_id,
                direction=msg.direction.value, message_type=msg.message_type.value,
                body=msg.body, status=msg.status.value, sent_at=msg.sent_at,
                created_at=msg.created_at,
            )
            session.add(m)
            conv_m = session.get(ConversationModel, conversation_id)
            if conv_m:
                conv_m.last_message_at = datetime.now(UTC)
            session.commit()
        self._activity_service.record(workspace_id, ActivityType.MESSAGE_SENT, contact_id=contact_id)
        return msg

    def list_messages(self, conversation_id: str, limit: int = 100) -> Sequence[MessageEntity]:
        from atlas_ultimate_crm.domain.enums.messaging import MessageType
        with self._session_factory() as session:
            stmt = select(MessageModel).where(MessageModel.conversation_id == conversation_id).order_by(MessageModel.created_at.asc()).limit(limit)
            models = session.scalars(stmt).all()
            return [
                MessageEntity(
                    id=m.id, workspace_id=m.workspace_id, conversation_id=m.conversation_id,
                    contact_id=m.contact_id, provider_message_id=m.provider_message_id,
                    direction=MessageDirection(m.direction), message_type=MessageType(m.message_type),
                    body=m.body, status=MessageStatus(m.status),
                    sent_at=m.sent_at, received_at=m.received_at, created_at=m.created_at,
                )
                for m in models
            ]

    def list_open_conversations(self, workspace_id: str) -> Sequence[ConversationEntity]:
        with self._session_factory() as session:
            return self._repo(session).list_open(workspace_id)

    def mark_read(self, conversation_id: str) -> None:
        with self._session_factory() as session:
            from atlas_ultimate_crm.infrastructure.database.models.conversations import (
                ConversationModel,
            )
            m = session.get(ConversationModel, conversation_id)
            if m:
                m.unread_count = 0
                session.commit()
