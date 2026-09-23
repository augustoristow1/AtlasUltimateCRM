import logging
from typing import Optional, Sequence

from atlas_ultimate_crm.application.event_bus import InMemoryEventBus
from atlas_ultimate_crm.domain.entities.company import CompanyEntity

logger = logging.getLogger(__name__)


class CompanyService:
    def __init__(self, event_bus: InMemoryEventBus, session_factory) -> None:
        self._event_bus = event_bus
        self._session_factory = session_factory

    def _repo(self, session):
        from atlas_ultimate_crm.infrastructure.database.repositories.company_repository import (
            SQLCompanyRepository,
        )
        return SQLCompanyRepository(session)

    def create_company(self, workspace_id: str, name: str, **kwargs) -> CompanyEntity:
        company = CompanyEntity(workspace_id=workspace_id, name=name, **kwargs)
        with self._session_factory() as session:
            saved = self._repo(session).save(company)
            session.commit()
        return saved

    def get_company(self, company_id: str) -> Optional[CompanyEntity]:
        with self._session_factory() as session:
            return self._repo(session).get_by_id(company_id)

    def list_companies(self, workspace_id: str, search: str = "", limit: int = 100) -> Sequence[CompanyEntity]:
        with self._session_factory() as session:
            return self._repo(session).list_by_workspace(workspace_id, search=search, limit=limit)

    def count_companies(self, workspace_id: str) -> int:
        with self._session_factory() as session:
            return self._repo(session).count_by_workspace(workspace_id)
