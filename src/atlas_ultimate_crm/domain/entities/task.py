import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

from atlas_ultimate_crm.domain.enums.tasks import TaskPriority, TaskStatus


@dataclass
class TaskEntity:
    workspace_id: str
    title: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    contact_id: Optional[str] = None
    deal_id: Optional[str] = None
    assigned_user_id: Optional[str] = None
    due_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
