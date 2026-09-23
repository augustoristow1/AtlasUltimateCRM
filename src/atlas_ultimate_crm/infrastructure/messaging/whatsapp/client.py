import logging

import httpx

from atlas_ultimate_crm.infrastructure.messaging.whatsapp.schemas import (
    WAMessage,
    WAMessageResponse,
)

logger = logging.getLogger(__name__)


class WhatsAppClient:
    def __init__(self, access_token: str, phone_number_id: str, api_version: str = "v19.0") -> None:
        self._token = access_token
        self._phone_number_id = phone_number_id
        self._base_url = f"https://graph.facebook.com/{api_version}"
        self._client = httpx.Client(timeout=30.0)

    def send_message(self, message: WAMessage) -> WAMessageResponse:
        url = f"{self._base_url}/{self._phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        response = self._client.post(url, headers=headers, content=message.model_dump_json(exclude_none=True))
        response.raise_for_status()
        return WAMessageResponse.model_validate(response.json())

    def get_templates(self, waba_id: str) -> list[dict]:
        url = f"{self._base_url}/{waba_id}/message_templates"
        headers = {"Authorization": f"Bearer {self._token}"}
        response = self._client.get(url, headers=headers, params={"limit": 100})
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])

    def close(self) -> None:
        self._client.close()
