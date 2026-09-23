from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional
import uuid
from atlas_ultimate_crm.domain.enums.messaging import ConversationStatus, ChannelType


@dataclass
class ConversationEntity:
    workspace_id: str
    contact_id: str
    channel: ChannelType
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    channel_account_id: Optional[str] = None
    status: ConversationStatus = ConversationStatus.OPEN
    last_message_at: Optional[datetime] = None
    last_inbound_at: Optional[datetime] = None
    service_window_expires_at: Optional[datetime] = None
    unread_count: int = 0
    assigned_user_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
