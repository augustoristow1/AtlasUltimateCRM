from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from atlas_ultimate_crm.infrastructure.database.base import Base


class CompanyModel(Base):
    __tablename__ = "companies"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    website: Mapped[str] = mapped_column(String, default="")
    phone: Mapped[str] = mapped_column(String, default="")
    email: Mapped[str] = mapped_column(String, default="")
    city: Mapped[str] = mapped_column(String, default="")
    state: Mapped[str] = mapped_column(String, default="")
    industry: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))


class ContactCompanyModel(Base):
    __tablename__ = "contact_companies"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    contact_id: Mapped[str] = mapped_column(String, ForeignKey("contacts.id"), nullable=False)
    company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id"), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    job_title: Mapped[str] = mapped_column(String, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
