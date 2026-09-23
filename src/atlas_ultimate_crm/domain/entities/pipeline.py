from dataclasses import dataclass, field
from datetime import datetime, UTC
import uuid


@dataclass
class PipelineEntity:
    workspace_id: str
    name: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    position: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class PipelineStageEntity:
    pipeline_id: str
    name: str
    position: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    probability: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
