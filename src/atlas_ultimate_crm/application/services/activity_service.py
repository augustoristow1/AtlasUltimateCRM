import logging
from typing import Sequence, Optional
import json

from atlas_ultimate_crm.domain.entities.activity import ActivityEntity
from atlas_ultimate_crm.domain.enums.activities import ActivityType
from atlas_ultimate_crm.infrastructure.database.models.activities import ActivityModel
from sqlalchemy.orm import Session
from sqlalchemy import select

logger = logging.getLogger(__name__)


class ActivityService:
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def record(self, workspace_id: str, activity_type: ActivityType,
               contact_id: Optional[str] = None, company_id: Optional[str] = None,
               deal_id: Optional[str] = None, metadata: Optional[dict] = None) -> ActivityEntity:
        entity = ActivityEntity(
            workspace_id=workspace_id,
            activity_type=activity_type,
            contact_id=contact_id,
            company_id=company_id,
            deal_id=deal_id,
            metadata=metadata or {},
        )
        with self._session_factory() as session:
            m = ActivityModel(
                id=entity.id,
                workspace_id=entity.workspace_id,
                activity_type=entity.activity_type.value,
                contact_id=entity.contact_id,
                company_id=entity.company_id,
                deal_id=entity.deal_id,
                metadata_json=json.dumps(entity.metadata),
                created_at=entity.created_at,
            )
            session.add(m)
            session.commit()
        return entity

    def list_for_contact(self, contact_id: str, limit: int = 50) -> Sequence[ActivityEntity]:
        with self._session_factory() as session:
            stmt = select(ActivityModel).where(
                ActivityModel.contact_id == contact_id
            ).order_by(ActivityModel.created_at.desc()).limit(limit)
            models = session.scalars(stmt).all()
            return [
                ActivityEntity(
                    id=m.id, workspace_id=m.workspace_id,
                    activity_type=ActivityType(m.activity_type),
                    contact_id=m.contact_id, company_id=m.company_id, deal_id=m.deal_id,
                    metadata=json.loads(m.metadata_json or "{}"),
                    created_at=m.created_at,
                )
                for m in models
            ]
