from datetime import UTC, datetime

from sqlalchemy import select

from atlas_ultimate_crm.domain.entities.contact import ContactEntity
from atlas_ultimate_crm.domain.entities.conversation import ConversationEntity
from atlas_ultimate_crm.infrastructure.database.models.contacts import WhatsAppOptInModel


class MessagingPolicyService:
    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def can_send_freeform(self, conversation: ConversationEntity) -> bool:
        """True if within 24h service window."""
        if not conversation.service_window_expires_at:
            return False
        return datetime.now(UTC) < conversation.service_window_expires_at

    def requires_template(self, conversation: ConversationEntity) -> bool:
        return not self.can_send_freeform(conversation)

    def can_start_business_conversation(self, contact: ContactEntity) -> bool:
        """Check if contact has opted in to WhatsApp messages."""
        with self._session_factory() as session:
            stmt = select(WhatsAppOptInModel).where(
                WhatsAppOptInModel.contact_id == contact.id,
                WhatsAppOptInModel.status == "active",
            )
            opt_in = session.scalars(stmt).first()
            return opt_in is not None

    def service_window_status(self, conversation: ConversationEntity) -> str:
        if self.can_send_freeform(conversation):
            expires = conversation.service_window_expires_at
            return f"Janela aberta até {expires.strftime('%d/%m %H:%M') if expires else ''}"
        return "Janela encerrada — template necessário"
