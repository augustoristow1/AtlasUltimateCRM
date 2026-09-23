from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from atlas_ultimate_crm.infrastructure.database.base import Base


class WhatsAppTemplateModel(Base):
    __tablename__ = "whatsapp_templates"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False)
    channel_account_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("channel_accounts.id"), nullable=True)
    external_id: Mapped[str] = mapped_column(String, default="")
    name: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, default="pt_BR")
    category: Mapped[str] = mapped_column(String, default="MARKETING")
    status: Mapped[str] = mapped_column(String, default="APPROVED")
    components_json: Mapped[str] = mapped_column(Text, default="[]")
    synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class CampaignModel(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    channel: Mapped[str] = mapped_column(String, default="whatsapp")
    template_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("whatsapp_templates.id"), nullable=True)
    status: Mapped[str] = mapped_column(String, default="draft")
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    paused_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class CampaignRecipientModel(Base):
    __tablename__ = "campaign_recipients"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String, ForeignKey("campaigns.id"), nullable=False, index=True)
    contact_id: Mapped[str] = mapped_column(String, ForeignKey("contacts.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    provider_message_id: Mapped[str] = mapped_column(String, default="")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str] = mapped_column(String, default="")
    replied_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
