from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import Mapped, mapped_column
from atlas_ultimate_crm.infrastructure.database.base import Base


class PipelineModel(Base):
    __tablename__ = "pipelines"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class PipelineStageModel(Base):
    __tablename__ = "pipeline_stages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    pipeline_id: Mapped[str] = mapped_column(String, ForeignKey("pipelines.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(default=0)
    probability: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class DealModel(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    pipeline_id: Mapped[str] = mapped_column(String, ForeignKey("pipelines.id"), nullable=False)
    stage_id: Mapped[str] = mapped_column(String, ForeignKey("pipeline_stages.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[float] = mapped_column(Float, default=0.0)
    currency: Mapped[str] = mapped_column(String, default="BRL")
    company_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("companies.id"), nullable=True)
    status: Mapped[str] = mapped_column(String, default="open")
    expected_close_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))


class DealContactModel(Base):
    __tablename__ = "deal_contacts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    deal_id: Mapped[str] = mapped_column(String, ForeignKey("deals.id"), nullable=False)
    contact_id: Mapped[str] = mapped_column(String, ForeignKey("contacts.id"), nullable=False)
    is_primary: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
