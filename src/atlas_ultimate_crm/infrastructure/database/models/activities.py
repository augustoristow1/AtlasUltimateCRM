from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from atlas_ultimate_crm.infrastructure.database.base import Base


class ActivityModel(Base):
    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    activity_type: Mapped[str] = mapped_column(String, nullable=False)
    contact_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("contacts.id"), nullable=True, index=True)
    company_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("companies.id"), nullable=True)
    deal_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("deals.id"), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    contact_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("contacts.id"), nullable=True)
    deal_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("deals.id"), nullable=True)
    assigned_user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    due_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    priority: Mapped[str] = mapped_column(String, default="medium")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))


class NoteModel(Base):
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    contact_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("contacts.id"), nullable=True)
    company_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("companies.id"), nullable=True)
    deal_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("deals.id"), nullable=True)
    created_by_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
