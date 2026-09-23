from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from atlas_ultimate_crm.infrastructure.database.base import Base


class ChannelAccountModel(Base):
    __tablename__ = "channel_accounts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False)
    channel_type: Mapped[str] = mapped_column(String, nullable=False)
    display_name: Mapped[str] = mapped_column(String, default="")
    external_account_id: Mapped[str] = mapped_column(String, default="")
    external_phone_number_id: Mapped[str] = mapped_column(String, default="")
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))


class ConversationModel(Base):
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    contact_id: Mapped[str] = mapped_column(String, ForeignKey("contacts.id"), nullable=False, index=True)
    channel_account_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("channel_accounts.id"), nullable=True)
    channel: Mapped[str] = mapped_column(String, default="whatsapp")
    status: Mapped[str] = mapped_column(String, default="open")
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_inbound_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    service_window_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    unread_count: Mapped[int] = mapped_column(Integer, default=0)
    assigned_user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))


class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False)
    conversation_id: Mapped[str] = mapped_column(String, ForeignKey("conversations.id"), nullable=False, index=True)
    contact_id: Mapped[str] = mapped_column(String, ForeignKey("contacts.id"), nullable=False)
    provider_message_id: Mapped[str] = mapped_column(String, default="", index=True)
    direction: Mapped[str] = mapped_column(String, nullable=False)
    message_type: Mapped[str] = mapped_column(String, default="text")
    body: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String, default="queued")
    reply_to_message_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    template_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    received_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failure_reason: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
