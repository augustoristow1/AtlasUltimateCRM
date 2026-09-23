from dataclasses import dataclass

from atlas_ultimate_crm.domain.events.base import DomainEvent


@dataclass
class DealCreated(DomainEvent):
    deal_id: str = ""
    workspace_id: str = ""
    contact_id: str = ""


@dataclass
class DealStageChanged(DomainEvent):
    deal_id: str = ""
    workspace_id: str = ""
    old_stage_id: str = ""
    new_stage_id: str = ""


@dataclass
class TaskCompleted(DomainEvent):
    task_id: str = ""
    workspace_id: str = ""
    contact_id: str = ""
