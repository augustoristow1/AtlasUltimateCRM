import logging
from datetime import UTC, datetime
from typing import Optional, Sequence

try:
    import phonenumbers
    HAS_PHONENUMBERS = True
except ImportError:
    HAS_PHONENUMBERS = False

from atlas_ultimate_crm.application.event_bus import InMemoryEventBus
from atlas_ultimate_crm.domain.entities.contact import ContactEntity
from atlas_ultimate_crm.domain.enums.contact import ContactSource
from atlas_ultimate_crm.domain.events.contacts import ContactCreated, ContactUpdated

logger = logging.getLogger(__name__)


def normalize_phone(phone: str, default_region: str = "BR") -> str:
    if not phone:
        return ""
    if not HAS_PHONENUMBERS:
        return phone.strip()
    try:
        parsed = phonenumbers.parse(phone, default_region)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return phone.strip()


class ContactService:
    def __init__(self, event_bus: InMemoryEventBus, session_factory) -> None:
        self._event_bus = event_bus
        self._session_factory = session_factory

    def _repo(self, session):
        from atlas_ultimate_crm.infrastructure.database.repositories.contact_repository import (
            SQLContactRepository,
        )
        return SQLContactRepository(session)

    def create_contact(self, workspace_id: str, name: str, phone: str = "", email: str = "",
                       source: ContactSource = ContactSource.MANUAL, **kwargs) -> ContactEntity:
        normalized = normalize_phone(phone)
        if phone and normalized:
            with self._session_factory() as session:
                existing = self._repo(session).get_by_phone(workspace_id, normalized)
                if existing:
                    return existing

        contact = ContactEntity(
            workspace_id=workspace_id,
            name=name,
            phone=phone,
            phone_normalized=normalized,
            email=email,
            source=source,
            **kwargs,
        )
        with self._session_factory() as session:
            saved = self._repo(session).save(contact)
            session.commit()

        self._event_bus.publish(ContactCreated(contact_id=saved.id, workspace_id=workspace_id, name=name, phone=phone))
        return saved

    def update_contact(self, contact_id: str, **kwargs) -> Optional[ContactEntity]:
        with self._session_factory() as session:
            contact = self._repo(session).get_by_id(contact_id)
            if not contact:
                return None
            for key, value in kwargs.items():
                if hasattr(contact, key):
                    setattr(contact, key, value)
            contact.updated_at = datetime.now(UTC)
            saved = self._repo(session).save(contact)
            session.commit()
        self._event_bus.publish(ContactUpdated(contact_id=contact_id, workspace_id=contact.workspace_id))
        return saved

    def get_contact(self, contact_id: str) -> Optional[ContactEntity]:
        with self._session_factory() as session:
            return self._repo(session).get_by_id(contact_id)

    def get_or_create_by_phone(self, workspace_id: str, phone: str, name: str = "") -> ContactEntity:
        normalized = normalize_phone(phone)
        with self._session_factory() as session:
            existing = self._repo(session).get_by_phone(workspace_id, normalized or phone)
            if existing:
                return existing
        return self.create_contact(
            workspace_id=workspace_id,
            name=name or phone,
            phone=phone,
            source=ContactSource.WHATSAPP_INBOUND,
        )

    def list_contacts(self, workspace_id: str, search: str = "", limit: int = 100, offset: int = 0) -> Sequence[ContactEntity]:
        with self._session_factory() as session:
            return self._repo(session).list_by_workspace(workspace_id, search=search, limit=limit, offset=offset)

    def count_contacts(self, workspace_id: str) -> int:
        with self._session_factory() as session:
            return self._repo(session).count_by_workspace(workspace_id)
