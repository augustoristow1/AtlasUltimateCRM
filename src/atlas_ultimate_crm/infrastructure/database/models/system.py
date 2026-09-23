from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from atlas_ultimate_crm.infrastructure.database.base import Base


class BackgroundJobModel(Base):
    __tablename__ = "background_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    job_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    result_json: Mapped[str] = mapped_column(Text, default="{}")
    error: Mapped[str] = mapped_column(String, default="")
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class WebhookEventModel(Base):
    __tablename__ = "webhook_events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    external_event_id: Mapped[str] = mapped_column(String, default="", index=True)
    event_type: Mapped[str] = mapped_column(String, default="")
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    received_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")
