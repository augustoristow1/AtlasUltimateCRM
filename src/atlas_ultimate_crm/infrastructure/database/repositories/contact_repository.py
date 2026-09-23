import uuid
from datetime import datetime, UTC
from typing import Sequence, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from atlas_ultimate_crm.domain.entities.contact import ContactEntity
from atlas_ultimate_crm.domain.enums.contact import LifecycleStage, ContactSource
from atlas_ultimate_crm.infrastructure.database.models.contacts import ContactModel


def _to_entity(m: ContactModel) -> ContactEntity:
    return ContactEntity(
        id=m.id,
        workspace_id=m.workspace_id,
        name=m.name,
        phone=m.phone,
        phone_normalized=m.phone_normalized,
        email=m.email,
        city=m.city,
        state=m.state,
        website=m.website,
        job_title=m.job_title,
        source=ContactSource(m.source),
        lifecycle_stage=LifecycleStage(m.lifecycle_stage),
        notes_summary=m.notes_summary,
        last_activity_at=m.last_activity_at,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _to_model(e: ContactEntity) -> ContactModel:
    return ContactModel(
        id=e.id,
        workspace_id=e.workspace_id,
        name=e.name,
        phone=e.phone,
        phone_normalized=e.phone_normalized,
        email=e.email,
        city=e.city,
        state=e.state,
        website=e.website,
        job_title=e.job_title,
        source=e.source.value,
        lifecycle_stage=e.lifecycle_stage.value,
        notes_summary=e.notes_summary,
        last_activity_at=e.last_activity_at,
        created_at=e.created_at,
        updated_at=e.updated_at,
    )


class SQLContactRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, contact_id: str) -> Optional[ContactEntity]:
        m = self._session.get(ContactModel, contact_id)
        return _to_entity(m) if m else None

    def get_by_phone(self, workspace_id: str, phone: str) -> Optional[ContactEntity]:
        stmt = select(ContactModel).where(
            ContactModel.workspace_id == workspace_id,
            or_(ContactModel.phone_normalized == phone, ContactModel.phone == phone),
        )
        m = self._session.scalars(stmt).first()
        return _to_entity(m) if m else None

    def list_by_workspace(self, workspace_id: str, search: str = "", limit: int = 100, offset: int = 0) -> Sequence[ContactEntity]:
        stmt = select(ContactModel).where(ContactModel.workspace_id == workspace_id)
        if search:
            like = f"%{search}%"
            stmt = stmt.where(or_(ContactModel.name.ilike(like), ContactModel.phone.ilike(like), ContactModel.email.ilike(like)))
        stmt = stmt.order_by(ContactModel.created_at.desc()).limit(limit).offset(offset)
        return [_to_entity(m) for m in self._session.scalars(stmt)]

    def count_by_workspace(self, workspace_id: str) -> int:
        stmt = select(func.count()).select_from(ContactModel).where(ContactModel.workspace_id == workspace_id)
        return self._session.scalar(stmt) or 0

    def save(self, contact: ContactEntity) -> ContactEntity:
        existing = self._session.get(ContactModel, contact.id)
        if existing:
            existing.name = contact.name
            existing.phone = contact.phone
            existing.phone_normalized = contact.phone_normalized
            existing.email = contact.email
            existing.city = contact.city
            existing.state = contact.state
            existing.website = contact.website
            existing.job_title = contact.job_title
            existing.source = contact.source.value
            existing.lifecycle_stage = contact.lifecycle_stage.value
            existing.notes_summary = contact.notes_summary
            existing.last_activity_at = contact.last_activity_at
            existing.updated_at = datetime.now(UTC)
            self._session.flush()
            return _to_entity(existing)
        else:
            m = _to_model(contact)
            self._session.add(m)
            self._session.flush()
            return contact

    def delete(self, contact_id: str) -> None:
        m = self._session.get(ContactModel, contact_id)
        if m:
            self._session.delete(m)
            self._session.flush()
