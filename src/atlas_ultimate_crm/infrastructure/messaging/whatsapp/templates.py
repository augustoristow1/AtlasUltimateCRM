from atlas_ultimate_crm.infrastructure.messaging.whatsapp.client import WhatsAppClient


class WhatsAppTemplateService:
    def __init__(self, client: WhatsAppClient, waba_id: str) -> None:
        self._client = client
        self._waba_id = waba_id

    def list_templates(self) -> list[dict]:
        return self._client.get_templates(self._waba_id)
