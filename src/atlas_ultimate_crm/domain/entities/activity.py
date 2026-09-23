import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

from atlas_ultimate_crm.domain.enums.activities import ActivityType


@dataclass
class ActivityEntity:
    workspace_id: str
    activity_type: ActivityType
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    contact_id: Optional[str] = None
    company_id: Optional[str] = None
    deal_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
