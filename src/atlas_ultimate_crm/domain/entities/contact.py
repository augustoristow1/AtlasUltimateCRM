from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import Optional
import uuid
from atlas_ultimate_crm.domain.enums.contact import LifecycleStage, ContactSource


@dataclass
class ContactEntity:
    workspace_id: str
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    phone: str = ""
    phone_normalized: str = ""
    email: str = ""
    city: str = ""
    state: str = ""
    website: str = ""
    job_title: str = ""
    source: ContactSource = ContactSource.MANUAL
    lifecycle_stage: LifecycleStage = LifecycleStage.LEAD
    notes_summary: str = ""
    last_activity_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
