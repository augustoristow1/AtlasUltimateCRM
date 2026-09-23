import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

from atlas_ultimate_crm.domain.enums.messaging import MessageDirection, MessageStatus, MessageType


@dataclass
class MessageEntity:
    workspace_id: str
    conversation_id: str
    contact_id: str
    direction: MessageDirection
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    provider_message_id: str = ""
    message_type: MessageType = MessageType.TEXT
    body: str = ""
    status: MessageStatus = MessageStatus.QUEUED
    reply_to_message_id: Optional[str] = None
    template_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    failure_reason: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
