from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from atlas_ultimate_crm.infrastructure.database.base import Base


class ContactModel(Base):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, default="")
    phone_normalized: Mapped[str] = mapped_column(String, default="", index=True)
    email: Mapped[str] = mapped_column(String, default="")
    city: Mapped[str] = mapped_column(String, default="")
    state: Mapped[str] = mapped_column(String, default="")
    website: Mapped[str] = mapped_column(String, default="")
    job_title: Mapped[str] = mapped_column(String, default="")
    source: Mapped[str] = mapped_column(String, default="manual")
    lifecycle_stage: Mapped[str] = mapped_column(String, default="lead")
    notes_summary: Mapped[str] = mapped_column(Text, default="")
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))


class TagModel(Base):
    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    color: Mapped[str] = mapped_column(String, default="#6366f1")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class ContactTagModel(Base):
    __tablename__ = "contact_tags"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    contact_id: Mapped[str] = mapped_column(String, ForeignKey("contacts.id"), nullable=False)
    tag_id: Mapped[str] = mapped_column(String, ForeignKey("tags.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class ContactListModel(Base):
    __tablename__ = "contact_lists"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class ContactListMemberModel(Base):
    __tablename__ = "contact_list_members"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    list_id: Mapped[str] = mapped_column(String, ForeignKey("contact_lists.id"), nullable=False)
    contact_id: Mapped[str] = mapped_column(String, ForeignKey("contacts.id"), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class WhatsAppOptInModel(Base):
    __tablename__ = "whatsapp_opt_ins"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False)
    contact_id: Mapped[str] = mapped_column(String, ForeignKey("contacts.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, default="active")
    source: Mapped[str] = mapped_column(String, default="manual")
    granted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
