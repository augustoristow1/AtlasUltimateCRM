import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class WorkspaceEntity:
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    slug: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class UserEntity:
    workspace_id: str
    name: str
    email: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: str = "owner"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
