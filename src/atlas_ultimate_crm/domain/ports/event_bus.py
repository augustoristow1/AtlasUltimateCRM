from typing import Callable, Protocol, Type

from atlas_ultimate_crm.domain.events.base import DomainEvent

EventHandler = Callable[[DomainEvent], None]


class EventBus(Protocol):
    def publish(self, event: DomainEvent) -> None: ...
    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None: ...
