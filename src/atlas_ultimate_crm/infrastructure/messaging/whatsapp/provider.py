import logging
import uuid

from atlas_ultimate_crm.domain.ports.messaging_provider import (
    MockTemplate,
    SendTextResult,
    TemplateComponent,
)
from atlas_ultimate_crm.infrastructure.messaging.whatsapp.client import WhatsAppClient
from atlas_ultimate_crm.infrastructure.messaging.whatsapp.schemas import (
    WAMessage,
    WATemplateBody,
    WATemplateComponent,
    WATemplateLanguage,
    WATextBody,
)

logger = logging.getLogger(__name__)


class WhatsAppCloudProvider:
    def __init__(self, client: WhatsAppClient, waba_id: str) -> None:
        self._client = client
        self._waba_id = waba_id

    def send_text(self, to_phone: str, body: str) -> SendTextResult:
        try:
            msg = WAMessage(to=to_phone, type="text", text=WATextBody(body=body))
            result = self._client.send_message(msg)
            msg_id = result.messages[0]["id"] if result.messages else str(uuid.uuid4())
            return SendTextResult(provider_message_id=msg_id, success=True)
        except Exception as e:
            logger.error("WhatsApp send_text failed: %s", e)
            return SendTextResult(provider_message_id="", success=False, error=str(e))

    def send_template(self, to_phone: str, template_name: str, language: str, components: list[TemplateComponent]) -> SendTextResult:
        try:
            wa_components = [WATemplateComponent(type=c.type, parameters=c.parameters) for c in components]
            template = WATemplateBody(
                name=template_name,
                language=WATemplateLanguage(code=language),
                components=wa_components,
            )
            msg = WAMessage(to=to_phone, type="template", template=template)
            result = self._client.send_message(msg)
            msg_id = result.messages[0]["id"] if result.messages else str(uuid.uuid4())
            return SendTextResult(provider_message_id=msg_id, success=True)
        except Exception as e:
            logger.error("WhatsApp send_template failed: %s", e)
            return SendTextResult(provider_message_id="", success=False, error=str(e))

    def get_templates(self) -> list[MockTemplate]:
        try:
            raw = self._client.get_templates(self._waba_id)
            return [
                MockTemplate(
                    external_id=t.get("id", ""),
                    name=t.get("name", ""),
                    language=t.get("language", "pt_BR"),
                    category=t.get("category", ""),
                    status=t.get("status", ""),
                    components=t.get("components", []),
                )
                for t in raw
            ]
        except Exception as e:
            logger.error("Failed to fetch templates: %s", e)
            return []

    def test_connection(self) -> bool:
        try:
            self._client.get_templates(self._waba_id)
            return True
        except Exception:
            return False

    def provider_name(self) -> str:
        return "WhatsApp Cloud API"
