from typing import Sequence, Optional
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from atlas_ultimate_crm.domain.entities.conversation import ConversationEntity
from atlas_ultimate_crm.domain.enums.messaging import ConversationStatus, ChannelType
from atlas_ultimate_crm.infrastructure.database.models.conversations import ConversationModel


def _to_entity(m: ConversationModel) -> ConversationEntity:
    return ConversationEntity(
        id=m.id, workspace_id=m.workspace_id, contact_id=m.contact_id,
        channel=ChannelType(m.channel), channel_account_id=m.channel_account_id,
        status=ConversationStatus(m.status), last_message_at=m.last_message_at,
        last_inbound_at=m.last_inbound_at, service_window_expires_at=m.service_window_expires_at,
        unread_count=m.unread_count, assigned_user_id=m.assigned_user_id,
        created_at=m.created_at, updated_at=m.updated_at,
    )


class SQLConversationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, conv_id: str) -> Optional[ConversationEntity]:
        m = self._session.get(ConversationModel, conv_id)
        return _to_entity(m) if m else None

    def get_by_contact(self, workspace_id: str, contact_id: str) -> Optional[ConversationEntity]:
        stmt = select(ConversationModel).where(
            ConversationModel.workspace_id == workspace_id,
            ConversationModel.contact_id == contact_id,
        ).order_by(ConversationModel.created_at.desc())
        m = self._session.scalars(stmt).first()
        return _to_entity(m) if m else None

    def list_open(self, workspace_id: str, limit: int = 50) -> Sequence[ConversationEntity]:
        stmt = select(ConversationModel).where(
            ConversationModel.workspace_id == workspace_id,
            ConversationModel.status == "open",
        ).order_by(ConversationModel.last_message_at.desc()).limit(limit)
        return [_to_entity(m) for m in self._session.scalars(stmt)]

    def count_open(self, workspace_id: str) -> int:
        stmt = select(func.count()).select_from(ConversationModel).where(
            ConversationModel.workspace_id == workspace_id,
            ConversationModel.status == "open",
        )
        return self._session.scalar(stmt) or 0

    def save(self, conv: ConversationEntity) -> ConversationEntity:
        existing = self._session.get(ConversationModel, conv.id)
        if existing:
            existing.status = conv.status.value
            existing.last_message_at = conv.last_message_at
            existing.last_inbound_at = conv.last_inbound_at
            existing.service_window_expires_at = conv.service_window_expires_at
            existing.unread_count = conv.unread_count
            existing.assigned_user_id = conv.assigned_user_id
            existing.updated_at = datetime.now(UTC)
            self._session.flush()
        else:
            m = ConversationModel(
                id=conv.id, workspace_id=conv.workspace_id, contact_id=conv.contact_id,
                channel_account_id=conv.channel_account_id, channel=conv.channel.value,
                status=conv.status.value, last_message_at=conv.last_message_at,
                last_inbound_at=conv.last_inbound_at, service_window_expires_at=conv.service_window_expires_at,
                unread_count=conv.unread_count, assigned_user_id=conv.assigned_user_id,
                created_at=conv.created_at, updated_at=conv.updated_at,
            )
            self._session.add(m)
            self._session.flush()
        return conv
