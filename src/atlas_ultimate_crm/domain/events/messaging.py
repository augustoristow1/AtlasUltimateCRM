from dataclasses import dataclass
from atlas_ultimate_crm.domain.events.base import DomainEvent


@dataclass
class MessageReceived(DomainEvent):
    message_id: str = ""
    conversation_id: str = ""
    contact_id: str = ""
    workspace_id: str = ""
    body: str = ""
    phone: str = ""


@dataclass
class MessageSent(DomainEvent):
    message_id: str = ""
    conversation_id: str = ""
    contact_id: str = ""
    workspace_id: str = ""


@dataclass
class MessageStatusChanged(DomainEvent):
    message_id: str = ""
    provider_message_id: str = ""
    new_status: str = ""
    workspace_id: str = ""
