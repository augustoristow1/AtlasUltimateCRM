import logging
import uuid
from typing import Sequence

from sqlalchemy import select

from atlas_ultimate_crm.core.constants import DEFAULT_PIPELINE_NAME
from atlas_ultimate_crm.domain.entities.pipeline import PipelineEntity, PipelineStageEntity
from atlas_ultimate_crm.infrastructure.database.models.pipelines import (
    PipelineModel,
    PipelineStageModel,
)

logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def get_or_create_default_pipeline(self, workspace_id: str) -> tuple[PipelineEntity, list[PipelineStageEntity]]:
        with self._session_factory() as session:
            stmt = select(PipelineModel).where(PipelineModel.workspace_id == workspace_id)
            pipeline_m = session.scalars(stmt).first()
            if pipeline_m:
                stages_m = session.scalars(
                    select(PipelineStageModel).where(PipelineStageModel.pipeline_id == pipeline_m.id).order_by(PipelineStageModel.position)
                ).all()
                pipeline = PipelineEntity(id=pipeline_m.id, workspace_id=workspace_id, name=pipeline_m.name)
                stages = [PipelineStageEntity(id=s.id, pipeline_id=s.pipeline_id, name=s.name, position=s.position) for s in stages_m]
                return pipeline, stages

            # Create default pipeline
            pipeline_id = str(uuid.uuid4())
            pipeline_m = PipelineModel(id=pipeline_id, workspace_id=workspace_id, name=DEFAULT_PIPELINE_NAME)
            session.add(pipeline_m)

            stage_names = ["Novo", "Contato feito", "Qualificado", "Proposta", "Negociação", "Ganho", "Perdido"]
            stage_models = []
            for i, name in enumerate(stage_names):
                s = PipelineStageModel(id=str(uuid.uuid4()), pipeline_id=pipeline_id, name=name, position=i)
                session.add(s)
                stage_models.append(s)
            session.commit()

            pipeline = PipelineEntity(id=pipeline_id, workspace_id=workspace_id, name=DEFAULT_PIPELINE_NAME)
            stages = [PipelineStageEntity(id=s.id, pipeline_id=pipeline_id, name=s.name, position=s.position) for s in stage_models]
            return pipeline, stages

    def list_pipelines(self, workspace_id: str) -> Sequence[PipelineEntity]:
        with self._session_factory() as session:
            stmt = select(PipelineModel).where(PipelineModel.workspace_id == workspace_id)
            return [PipelineEntity(id=m.id, workspace_id=workspace_id, name=m.name) for m in session.scalars(stmt)]

    def list_stages(self, pipeline_id: str) -> Sequence[PipelineStageEntity]:
        with self._session_factory() as session:
            stmt = select(PipelineStageModel).where(PipelineStageModel.pipeline_id == pipeline_id).order_by(PipelineStageModel.position)
            return [PipelineStageEntity(id=m.id, pipeline_id=pipeline_id, name=m.name, position=m.position) for m in session.scalars(stmt)]
