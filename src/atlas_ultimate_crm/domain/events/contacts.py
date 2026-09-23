from dataclasses import dataclass

from atlas_ultimate_crm.domain.events.base import DomainEvent


@dataclass
class ContactCreated(DomainEvent):
    contact_id: str = ""
    workspace_id: str = ""
    name: str = ""
    phone: str = ""


@dataclass
class ContactUpdated(DomainEvent):
    contact_id: str = ""
    workspace_id: str = ""
