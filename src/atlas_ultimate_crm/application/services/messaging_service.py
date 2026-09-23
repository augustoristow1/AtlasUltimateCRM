import logging

from atlas_ultimate_crm.application.services.conversation_service import ConversationService
from atlas_ultimate_crm.domain.enums.messaging import ChannelType
from atlas_ultimate_crm.domain.ports.messaging_provider import MessagingProvider

logger = logging.getLogger(__name__)


class MessagingService:
    def __init__(self, provider: MessagingProvider, conv_service: ConversationService) -> None:
        self._provider = provider
        self._conv_service = conv_service

    def send_text_to_contact(self, workspace_id: str, contact_id: str, phone: str, body: str) -> bool:
        result = self._provider.send_text(phone, body)
        conv = self._conv_service.get_or_create_conversation(workspace_id, contact_id, ChannelType.WHATSAPP)
        self._conv_service.save_outbound_message(
            workspace_id=workspace_id,
            conversation_id=conv.id,
            contact_id=contact_id,
            body=body,
            provider_message_id=result.provider_message_id,
        )
        return result.success

    def handle_inbound(self, workspace_id: str, contact_id: str, phone: str, body: str, provider_message_id: str = "") -> None:
        conv = self._conv_service.get_or_create_conversation(workspace_id, contact_id, ChannelType.WHATSAPP)
        self._conv_service.save_inbound_message(
            workspace_id=workspace_id,
            conversation_id=conv.id,
            contact_id=contact_id,
            body=body,
            provider_message_id=provider_message_id,
        )

    def get_templates(self):
        return self._provider.get_templates()

    def provider_name(self) -> str:
        return self._provider.provider_name()
