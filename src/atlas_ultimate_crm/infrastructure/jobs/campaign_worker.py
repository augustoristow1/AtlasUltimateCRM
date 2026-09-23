import logging
from datetime import datetime, UTC

logger = logging.getLogger(__name__)


class CampaignWorker:
    """Processes campaign sending jobs."""

    def __init__(self, campaign_service, messaging_service) -> None:
        self._campaign_service = campaign_service
        self._messaging_service = messaging_service

    def process_campaign(self, campaign_id: str, workspace_id: str) -> None:
        logger.info("Processing campaign %s", campaign_id)
        try:
            self._campaign_service.run_campaign(campaign_id, workspace_id)
        except Exception as e:
            logger.error("Campaign %s failed: %s", campaign_id, e)
