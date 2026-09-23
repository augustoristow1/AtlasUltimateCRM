from typing import Any, Optional

from pydantic import BaseModel


class WATextBody(BaseModel):
    body: str


class WATemplateLanguage(BaseModel):
    code: str


class WATemplateComponent(BaseModel):
    type: str
    parameters: list[dict[str, Any]] = []


class WATemplateBody(BaseModel):
    name: str
    language: WATemplateLanguage
    components: list[WATemplateComponent] = []


class WAMessage(BaseModel):
    messaging_product: str = "whatsapp"
    recipient_type: str = "individual"
    to: str
    type: str
    text: Optional[WATextBody] = None
    template: Optional[WATemplateBody] = None


class WAMessageResponse(BaseModel):
    messages: list[dict[str, str]] = []
    contacts: list[dict[str, str]] = []


class WAWebhookEntry(BaseModel):
    id: str
    changes: list[dict[str, Any]]


class WAWebhookPayload(BaseModel):
    object: str
    entry: list[WAWebhookEntry]
