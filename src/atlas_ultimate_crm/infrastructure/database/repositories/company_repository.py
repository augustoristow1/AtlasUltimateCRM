from typing import Sequence, Optional
from datetime import datetime, UTC
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from atlas_ultimate_crm.domain.entities.company import CompanyEntity
from atlas_ultimate_crm.infrastructure.database.models.companies import CompanyModel


def _to_entity(m: CompanyModel) -> CompanyEntity:
    return CompanyEntity(
        id=m.id, workspace_id=m.workspace_id, name=m.name,
        website=m.website, phone=m.phone, email=m.email,
        city=m.city, state=m.state, industry=m.industry,
        created_at=m.created_at, updated_at=m.updated_at,
    )


class SQLCompanyRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, company_id: str) -> Optional[CompanyEntity]:
        m = self._session.get(CompanyModel, company_id)
        return _to_entity(m) if m else None

    def list_by_workspace(self, workspace_id: str, search: str = "", limit: int = 100, offset: int = 0) -> Sequence[CompanyEntity]:
        stmt = select(CompanyModel).where(CompanyModel.workspace_id == workspace_id)
        if search:
            like = f"%{search}%"
            stmt = stmt.where(or_(CompanyModel.name.ilike(like)))
        stmt = stmt.order_by(CompanyModel.created_at.desc()).limit(limit).offset(offset)
        return [_to_entity(m) for m in self._session.scalars(stmt)]

    def count_by_workspace(self, workspace_id: str) -> int:
        stmt = select(func.count()).select_from(CompanyModel).where(CompanyModel.workspace_id == workspace_id)
        return self._session.scalar(stmt) or 0

    def save(self, company: CompanyEntity) -> CompanyEntity:
        existing = self._session.get(CompanyModel, company.id)
        if existing:
            existing.name = company.name
            existing.website = company.website
            existing.phone = company.phone
            existing.email = company.email
            existing.city = company.city
            existing.state = company.state
            existing.industry = company.industry
            existing.updated_at = datetime.now(UTC)
            self._session.flush()
        else:
            m = CompanyModel(
                id=company.id, workspace_id=company.workspace_id, name=company.name,
                website=company.website, phone=company.phone, email=company.email,
                city=company.city, state=company.state, industry=company.industry,
                created_at=company.created_at, updated_at=company.updated_at,
            )
            self._session.add(m)
            self._session.flush()
        return company
