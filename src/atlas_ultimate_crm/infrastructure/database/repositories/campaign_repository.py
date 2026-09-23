from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from atlas_ultimate_crm.domain.entities.campaign import CampaignEntity, CampaignRecipientEntity
from atlas_ultimate_crm.domain.enums.campaigns import CampaignStatus, RecipientStatus
from atlas_ultimate_crm.infrastructure.database.models.campaigns import (
    CampaignModel,
    CampaignRecipientModel,
)


def _campaign_to_entity(m: CampaignModel) -> CampaignEntity:
    return CampaignEntity(
        id=m.id, workspace_id=m.workspace_id, name=m.name, channel=m.channel,
        template_id=m.template_id, status=CampaignStatus(m.status),
        scheduled_at=m.scheduled_at, started_at=m.started_at,
        paused_at=m.paused_at, completed_at=m.completed_at, created_at=m.created_at,
    )


def _recipient_to_entity(m: CampaignRecipientModel) -> CampaignRecipientEntity:
    return CampaignRecipientEntity(
        id=m.id, campaign_id=m.campaign_id, contact_id=m.contact_id,
        status=RecipientStatus(m.status), scheduled_at=m.scheduled_at,
        sent_at=m.sent_at, provider_message_id=m.provider_message_id,
        attempts=m.attempts, error=m.error, replied_at=m.replied_at, created_at=m.created_at,
    )


class SQLCampaignRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, campaign_id: str) -> Optional[CampaignEntity]:
        m = self._session.get(CampaignModel, campaign_id)
        return _campaign_to_entity(m) if m else None

    def list_by_workspace(self, workspace_id: str) -> Sequence[CampaignEntity]:
        stmt = select(CampaignModel).where(CampaignModel.workspace_id == workspace_id).order_by(CampaignModel.created_at.desc())
        return [_campaign_to_entity(m) for m in self._session.scalars(stmt)]

    def count_active(self, workspace_id: str) -> int:
        stmt = select(func.count()).select_from(CampaignModel).where(
            CampaignModel.workspace_id == workspace_id, CampaignModel.status == "running"
        )
        return self._session.scalar(stmt) or 0

    def save_campaign(self, campaign: CampaignEntity) -> CampaignEntity:
        existing = self._session.get(CampaignModel, campaign.id)
        if existing:
            existing.name = campaign.name
            existing.status = campaign.status.value
            existing.template_id = campaign.template_id
            existing.scheduled_at = campaign.scheduled_at
            existing.started_at = campaign.started_at
            existing.paused_at = campaign.paused_at
            existing.completed_at = campaign.completed_at
            self._session.flush()
        else:
            m = CampaignModel(
                id=campaign.id, workspace_id=campaign.workspace_id, name=campaign.name,
                channel=campaign.channel, template_id=campaign.template_id,
                status=campaign.status.value, scheduled_at=campaign.scheduled_at,
                started_at=campaign.started_at, paused_at=campaign.paused_at,
                completed_at=campaign.completed_at, created_at=campaign.created_at,
            )
            self._session.add(m)
            self._session.flush()
        return campaign

    def get_recipients(self, campaign_id: str) -> Sequence[CampaignRecipientEntity]:
        stmt = select(CampaignRecipientModel).where(CampaignRecipientModel.campaign_id == campaign_id)
        return [_recipient_to_entity(m) for m in self._session.scalars(stmt)]

    def save_recipient(self, recipient: CampaignRecipientEntity) -> CampaignRecipientEntity:
        existing = self._session.get(CampaignRecipientModel, recipient.id)
        if existing:
            existing.status = recipient.status.value
            existing.sent_at = recipient.sent_at
            existing.provider_message_id = recipient.provider_message_id
            existing.attempts = recipient.attempts
            existing.error = recipient.error
            existing.replied_at = recipient.replied_at
            self._session.flush()
        else:
            m = CampaignRecipientModel(
                id=recipient.id, campaign_id=recipient.campaign_id, contact_id=recipient.contact_id,
                status=recipient.status.value, scheduled_at=recipient.scheduled_at,
                sent_at=recipient.sent_at, provider_message_id=recipient.provider_message_id,
                attempts=recipient.attempts, error=recipient.error, replied_at=recipient.replied_at,
                created_at=recipient.created_at,
            )
            self._session.add(m)
            self._session.flush()
        return recipient

    def find_pending_recipient_by_provider_msg(self, provider_message_id: str) -> Optional[CampaignRecipientEntity]:
        stmt = select(CampaignRecipientModel).where(
            CampaignRecipientModel.provider_message_id == provider_message_id
        )
        m = self._session.scalars(stmt).first()
        return _recipient_to_entity(m) if m else None
