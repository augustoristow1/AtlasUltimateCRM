import logging
from datetime import UTC, datetime
from typing import Sequence

from atlas_ultimate_crm.application.event_bus import InMemoryEventBus
from atlas_ultimate_crm.application.services.activity_service import ActivityService
from atlas_ultimate_crm.core.config import AppMode, get_settings
from atlas_ultimate_crm.domain.entities.campaign import CampaignEntity, CampaignRecipientEntity
from atlas_ultimate_crm.domain.enums.activities import ActivityType
from atlas_ultimate_crm.domain.enums.campaigns import CampaignStatus, RecipientStatus

logger = logging.getLogger(__name__)


class CampaignService:
    def __init__(self, event_bus: InMemoryEventBus, session_factory,
                 activity_service: ActivityService, messaging_service) -> None:
        self._event_bus = event_bus
        self._session_factory = session_factory
        self._activity_service = activity_service
        self._messaging_service = messaging_service

    def _repo(self, session):
        from atlas_ultimate_crm.infrastructure.database.repositories.campaign_repository import (
            SQLCampaignRepository,
        )
        return SQLCampaignRepository(session)

    def create_campaign(self, workspace_id: str, name: str, template_id: str | None = None) -> CampaignEntity:
        campaign = CampaignEntity(workspace_id=workspace_id, name=name, template_id=template_id)
        with self._session_factory() as session:
            saved = self._repo(session).save_campaign(campaign)
            session.commit()
        return saved

    def add_recipients(self, campaign_id: str, contact_ids: list[str]) -> list[CampaignRecipientEntity]:
        recipients = []
        with self._session_factory() as session:
            for contact_id in contact_ids:
                r = CampaignRecipientEntity(campaign_id=campaign_id, contact_id=contact_id)
                self._repo(session).save_recipient(r)
                recipients.append(r)
            session.commit()
        return recipients

    def run_campaign(self, campaign_id: str, workspace_id: str) -> None:
        """Execute campaign - send template messages to all pending recipients.

        Only available in mock mode. Real Meta API sends are blocked to prevent
        accidental mass messaging during development and testing.
        """
        settings = get_settings()
        if settings.app_mode == AppMode.META:
            raise RuntimeError(
                "Campaign execution is blocked in META mode. "
                "Use the WhatsApp Business Manager to send real campaigns."
            )

        with self._session_factory() as session:
            campaign = self._repo(session).get_by_id(campaign_id)
            if not campaign:
                return

        with self._session_factory() as session:
            from atlas_ultimate_crm.infrastructure.database.models.campaigns import CampaignModel
            cm = session.get(CampaignModel, campaign_id)
            if cm:
                cm.status = CampaignStatus.RUNNING.value
                cm.started_at = datetime.now(UTC)
                session.commit()

        with self._session_factory() as session:
            recipients = self._repo(session).get_recipients(campaign_id)

        for recipient in recipients:
            if recipient.status != RecipientStatus.PENDING:
                continue
            self._send_to_recipient(campaign, recipient, workspace_id)

        with self._session_factory() as session:
            from atlas_ultimate_crm.infrastructure.database.models.campaigns import CampaignModel
            cm = session.get(CampaignModel, campaign_id)
            if cm:
                cm.status = CampaignStatus.COMPLETED.value
                cm.completed_at = datetime.now(UTC)
                session.commit()

    def _send_to_recipient(self, campaign: CampaignEntity, recipient: CampaignRecipientEntity, workspace_id: str) -> None:
        from atlas_ultimate_crm.infrastructure.database.models.contacts import ContactModel
        with self._session_factory() as session:
            contact_m = session.get(ContactModel, recipient.contact_id)
            if not contact_m or not contact_m.phone:
                self._update_recipient_status(recipient.id, RecipientStatus.SKIPPED)
                return
            phone = contact_m.phone_normalized or contact_m.phone

        try:
            result = self._messaging_service._provider.send_text(phone, f"[Campanha: {campaign.name}]")
            status = RecipientStatus.SENT if result.success else RecipientStatus.FAILED
            self._update_recipient_status(recipient.id, status, provider_message_id=result.provider_message_id, error=result.error)
            self._activity_service.record(workspace_id, ActivityType.CAMPAIGN_MESSAGE_SENT, contact_id=recipient.contact_id)
        except Exception as e:
            self._update_recipient_status(recipient.id, RecipientStatus.FAILED, error=str(e))

    def _update_recipient_status(self, recipient_id: str, status: RecipientStatus,
                                  provider_message_id: str = "", error: str = "") -> None:
        with self._session_factory() as session:
            from atlas_ultimate_crm.infrastructure.database.models.campaigns import (
                CampaignRecipientModel,
            )
            m = session.get(CampaignRecipientModel, recipient_id)
            if m:
                m.status = status.value
                if provider_message_id:
                    m.provider_message_id = provider_message_id
                if status == RecipientStatus.SENT:
                    m.sent_at = datetime.now(UTC)
                if error:
                    m.error = error
                m.attempts = (m.attempts or 0) + 1
                session.commit()

    def mark_replied(self, provider_message_id: str) -> None:
        """Called when a contact replies to a campaign message."""
        with self._session_factory() as session:
            recipient = self._repo(session).find_pending_recipient_by_provider_msg(provider_message_id)
            if not recipient:
                return
        self._update_recipient_status(recipient.id, RecipientStatus.REPLIED)
        with self._session_factory() as session:
            from atlas_ultimate_crm.infrastructure.database.models.campaigns import (
                CampaignRecipientModel,
            )
            m = session.get(CampaignRecipientModel, recipient.id)
            if m:
                m.replied_at = datetime.now(UTC)
                session.commit()

    def list_campaigns(self, workspace_id: str) -> Sequence[CampaignEntity]:
        with self._session_factory() as session:
            return self._repo(session).list_by_workspace(workspace_id)

    def count_active(self, workspace_id: str) -> int:
        with self._session_factory() as session:
            return self._repo(session).count_active(workspace_id)
