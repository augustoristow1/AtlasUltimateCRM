from typing import Protocol
from dataclasses import dataclass


@dataclass
class SendTextResult:
    provider_message_id: str
    success: bool
    error: str = ""


@dataclass
class TemplateComponent:
    type: str
    parameters: list[dict]


@dataclass
class MockTemplate:
    external_id: str
    name: str
    language: str
    category: str
    status: str
    components: list[dict]


class MessagingProvider(Protocol):
    def send_text(self, to_phone: str, body: str) -> SendTextResult: ...
    def send_template(self, to_phone: str, template_name: str, language: str, components: list[TemplateComponent]) -> SendTextResult: ...
    def get_templates(self) -> list[MockTemplate]: ...
    def test_connection(self) -> bool: ...
    def provider_name(self) -> str: ...
