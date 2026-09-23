import logging
from typing import Sequence, Optional

from atlas_ultimate_crm.domain.entities.company import CompanyEntity
from atlas_ultimate_crm.infrastructure.database.repositories.company_repository import SQLCompanyRepository
from atlas_ultimate_crm.application.event_bus import InMemoryEventBus

logger = logging.getLogger(__name__)


class CompanyService:
    def __init__(self, repo: SQLCompanyRepository, event_bus: InMemoryEventBus, session_factory) -> None:
        self._repo = repo
        self._event_bus = event_bus
        self._session_factory = session_factory

    def create_company(self, workspace_id: str, name: str, **kwargs) -> CompanyEntity:
        company = CompanyEntity(workspace_id=workspace_id, name=name, **kwargs)
        with self._session_factory() as session:
            from atlas_ultimate_crm.infrastructure.database.repositories.company_repository import SQLCompanyRepository as Repo
            repo = Repo(session)
            saved = repo.save(company)
            session.commit()
        return saved

    def get_company(self, company_id: str) -> Optional[CompanyEntity]:
        return self._repo.get_by_id(company_id)

    def list_companies(self, workspace_id: str, search: str = "", limit: int = 100) -> Sequence[CompanyEntity]:
        return self._repo.list_by_workspace(workspace_id, search=search, limit=limit)

    def count_companies(self, workspace_id: str) -> int:
        return self._repo.count_by_workspace(workspace_id)
