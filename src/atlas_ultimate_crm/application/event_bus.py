import logging
from collections import defaultdict
from typing import Callable, Type
from atlas_ultimate_crm.domain.events.base import DomainEvent

logger = logging.getLogger(__name__)

EventHandler = Callable[[DomainEvent], None]


class InMemoryEventBus:
    """Simple synchronous in-process event bus."""

    def __init__(self) -> None:
        self._handlers: dict[type, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(type(event), [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error("Handler %s failed for event %s: %s", handler, type(event).__name__, e)
