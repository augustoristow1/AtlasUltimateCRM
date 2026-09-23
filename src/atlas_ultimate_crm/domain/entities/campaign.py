import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

from atlas_ultimate_crm.domain.enums.campaigns import CampaignStatus, RecipientStatus


@dataclass
class CampaignEntity:
    workspace_id: str
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    channel: str = "whatsapp"
    template_id: Optional[str] = None
    status: CampaignStatus = CampaignStatus.DRAFT
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class CampaignRecipientEntity:
    campaign_id: str
    contact_id: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: RecipientStatus = RecipientStatus.PENDING
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    provider_message_id: str = ""
    attempts: int = 0
    error: str = ""
    replied_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
