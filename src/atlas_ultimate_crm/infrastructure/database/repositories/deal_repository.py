from datetime import UTC, datetime
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from atlas_ultimate_crm.domain.entities.deal import DealEntity
from atlas_ultimate_crm.domain.enums.deals import DealStatus
from atlas_ultimate_crm.infrastructure.database.models.pipelines import DealModel


def _to_entity(m: DealModel) -> DealEntity:
    return DealEntity(
        id=m.id, workspace_id=m.workspace_id, pipeline_id=m.pipeline_id,
        stage_id=m.stage_id, title=m.title, value=m.value, currency=m.currency,
        company_id=m.company_id, status=DealStatus(m.status),
        expected_close_at=m.expected_close_at, created_at=m.created_at, updated_at=m.updated_at,
    )


class SQLDealRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, deal_id: str) -> Optional[DealEntity]:
        m = self._session.get(DealModel, deal_id)
        return _to_entity(m) if m else None

    def list_by_workspace(self, workspace_id: str) -> Sequence[DealEntity]:
        stmt = select(DealModel).where(DealModel.workspace_id == workspace_id, DealModel.status == "open").order_by(DealModel.created_at.desc())
        return [_to_entity(m) for m in self._session.scalars(stmt)]

    def list_by_stage(self, stage_id: str) -> Sequence[DealEntity]:
        stmt = select(DealModel).where(DealModel.stage_id == stage_id, DealModel.status == "open")
        return [_to_entity(m) for m in self._session.scalars(stmt)]

    def count_open(self, workspace_id: str) -> int:
        stmt = select(func.count()).select_from(DealModel).where(DealModel.workspace_id == workspace_id, DealModel.status == "open")
        return self._session.scalar(stmt) or 0

    def total_value(self, workspace_id: str) -> float:
        from sqlalchemy import func as sqlfunc
        stmt = select(sqlfunc.sum(DealModel.value)).where(DealModel.workspace_id == workspace_id, DealModel.status == "open")
        return self._session.scalar(stmt) or 0.0

    def save(self, deal: DealEntity) -> DealEntity:
        existing = self._session.get(DealModel, deal.id)
        if existing:
            existing.stage_id = deal.stage_id
            existing.title = deal.title
            existing.value = deal.value
            existing.currency = deal.currency
            existing.company_id = deal.company_id
            existing.status = deal.status.value
            existing.expected_close_at = deal.expected_close_at
            existing.updated_at = datetime.now(UTC)
            self._session.flush()
        else:
            m = DealModel(
                id=deal.id, workspace_id=deal.workspace_id, pipeline_id=deal.pipeline_id,
                stage_id=deal.stage_id, title=deal.title, value=deal.value, currency=deal.currency,
                company_id=deal.company_id, status=deal.status.value,
                expected_close_at=deal.expected_close_at, created_at=deal.created_at, updated_at=deal.updated_at,
            )
            self._session.add(m)
            self._session.flush()
        return deal
