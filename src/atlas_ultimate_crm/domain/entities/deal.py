from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional
import uuid
from atlas_ultimate_crm.domain.enums.deals import DealStatus


@dataclass
class DealEntity:
    workspace_id: str
    pipeline_id: str
    stage_id: str
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    value: float = 0.0
    currency: str = "BRL"
    company_id: Optional[str] = None
    status: DealStatus = DealStatus.OPEN
    expected_close_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
