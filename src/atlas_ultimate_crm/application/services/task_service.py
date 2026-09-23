import logging
from datetime import UTC, datetime
from typing import Optional, Sequence

from sqlalchemy import select

from atlas_ultimate_crm.application.event_bus import InMemoryEventBus
from atlas_ultimate_crm.domain.entities.task import TaskEntity
from atlas_ultimate_crm.domain.enums.tasks import TaskPriority, TaskStatus
from atlas_ultimate_crm.domain.events.deals import TaskCompleted
from atlas_ultimate_crm.infrastructure.database.models.activities import TaskModel

logger = logging.getLogger(__name__)


class TaskService:
    def __init__(self, session_factory, event_bus: InMemoryEventBus) -> None:
        self._session_factory = session_factory
        self._event_bus = event_bus

    def create_task(self, workspace_id: str, title: str, contact_id: Optional[str] = None,
                    deal_id: Optional[str] = None, due_at: Optional[datetime] = None,
                    priority: TaskPriority = TaskPriority.MEDIUM) -> TaskEntity:
        entity = TaskEntity(
            workspace_id=workspace_id, title=title, contact_id=contact_id,
            deal_id=deal_id, due_at=due_at, priority=priority,
        )
        with self._session_factory() as session:
            m = TaskModel(
                id=entity.id, workspace_id=entity.workspace_id, title=entity.title,
                description=entity.description, contact_id=entity.contact_id,
                deal_id=entity.deal_id, assigned_user_id=entity.assigned_user_id,
                due_at=entity.due_at, status=entity.status.value, priority=entity.priority.value,
                created_at=entity.created_at, updated_at=entity.updated_at,
            )
            session.add(m)
            session.commit()
        return entity

    def complete_task(self, task_id: str) -> Optional[TaskEntity]:
        with self._session_factory() as session:
            m = session.get(TaskModel, task_id)
            if not m:
                return None
            m.status = TaskStatus.COMPLETED.value
            m.completed_at = datetime.now(UTC)
            session.commit()
            entity = TaskEntity(
                id=m.id, workspace_id=m.workspace_id, title=m.title,
                contact_id=m.contact_id, deal_id=m.deal_id,
                status=TaskStatus.COMPLETED, completed_at=m.completed_at,
            )
        self._event_bus.publish(TaskCompleted(task_id=task_id, workspace_id=entity.workspace_id, contact_id=entity.contact_id or ""))
        return entity

    def list_tasks(self, workspace_id: str, status: Optional[TaskStatus] = None) -> Sequence[TaskEntity]:
        with self._session_factory() as session:
            stmt = select(TaskModel).where(TaskModel.workspace_id == workspace_id)
            if status:
                stmt = stmt.where(TaskModel.status == status.value)
            stmt = stmt.order_by(TaskModel.due_at.asc())
            models = session.scalars(stmt).all()
            return [
                TaskEntity(
                    id=m.id, workspace_id=m.workspace_id, title=m.title,
                    description=m.description, contact_id=m.contact_id,
                    deal_id=m.deal_id, due_at=m.due_at, completed_at=m.completed_at,
                    status=TaskStatus(m.status), priority=TaskPriority(m.priority),
                    created_at=m.created_at,
                )
                for m in models
            ]

    def count_pending(self, workspace_id: str) -> int:
        with self._session_factory() as session:
            from sqlalchemy import func
            from sqlalchemy import select as sel
            stmt = sel(func.count()).select_from(TaskModel).where(
                TaskModel.workspace_id == workspace_id,
                TaskModel.status == TaskStatus.PENDING.value,
            )
            return session.scalar(stmt) or 0
