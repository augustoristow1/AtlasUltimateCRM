import logging
from typing import Sequence, Optional

from atlas_ultimate_crm.domain.entities.deal import DealEntity
from atlas_ultimate_crm.domain.events.deals import DealCreated, DealStageChanged
from atlas_ultimate_crm.infrastructure.database.repositories.deal_repository import SQLDealRepository
from atlas_ultimate_crm.application.event_bus import InMemoryEventBus
from atlas_ultimate_crm.application.services.activity_service import ActivityService
from atlas_ultimate_crm.domain.enums.activities import ActivityType

logger = logging.getLogger(__name__)


class DealService:
    def __init__(self, repo: SQLDealRepository, event_bus: InMemoryEventBus,
                 session_factory, activity_service: ActivityService) -> None:
        self._repo = repo
        self._event_bus = event_bus
        self._session_factory = session_factory
        self._activity_service = activity_service

    def create_deal(self, workspace_id: str, pipeline_id: str, stage_id: str,
                    title: str, contact_id: Optional[str] = None, **kwargs) -> DealEntity:
        deal = DealEntity(workspace_id=workspace_id, pipeline_id=pipeline_id,
                          stage_id=stage_id, title=title, **kwargs)
        with self._session_factory() as session:
            from atlas_ultimate_crm.infrastructure.database.repositories.deal_repository import SQLDealRepository as Repo
            repo = Repo(session)
            saved = repo.save(deal)
            if contact_id:
                from atlas_ultimate_crm.infrastructure.database.models.pipelines import DealContactModel
                import uuid
                dc = DealContactModel(id=str(uuid.uuid4()), deal_id=deal.id, contact_id=contact_id, is_primary=True)
                session.add(dc)
            session.commit()
        self._event_bus.publish(DealCreated(deal_id=deal.id, workspace_id=workspace_id, contact_id=contact_id or ""))
        self._activity_service.record(workspace_id, ActivityType.DEAL_CREATED, contact_id=contact_id, deal_id=deal.id)
        return saved

    def change_stage(self, deal_id: str, new_stage_id: str) -> Optional[DealEntity]:
        deal = self._repo.get_by_id(deal_id)
        if not deal:
            return None
        old_stage_id = deal.stage_id
        deal.stage_id = new_stage_id
        with self._session_factory() as session:
            from atlas_ultimate_crm.infrastructure.database.repositories.deal_repository import SQLDealRepository as Repo
            repo = Repo(session)
            saved = repo.save(deal)
            session.commit()
        self._event_bus.publish(DealStageChanged(deal_id=deal_id, workspace_id=deal.workspace_id, old_stage_id=old_stage_id, new_stage_id=new_stage_id))
        self._activity_service.record(deal.workspace_id, ActivityType.DEAL_STAGE_CHANGED, deal_id=deal_id, metadata={"old_stage": old_stage_id, "new_stage": new_stage_id})
        return saved

    def list_deals(self, workspace_id: str) -> Sequence[DealEntity]:
        return self._repo.list_by_workspace(workspace_id)

    def count_open(self, workspace_id: str) -> int:
        return self._repo.count_open(workspace_id)

    def total_pipeline_value(self, workspace_id: str) -> float:
        return self._repo.total_value(workspace_id)
