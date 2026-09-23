from dataclasses import dataclass, field
from datetime import datetime, UTC
import uuid


@dataclass
class CompanyEntity:
    workspace_id: str
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    website: str = ""
    phone: str = ""
    email: str = ""
    city: str = ""
    state: str = ""
    industry: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
