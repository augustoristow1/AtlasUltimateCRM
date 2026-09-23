import uuid

from atlas_ultimate_crm.domain.ports.messaging_provider import (
    MockTemplate,
    SendTextResult,
    TemplateComponent,
)

MOCK_TEMPLATES = [
    MockTemplate(
        external_id="mock_boas_vindas",
        name="boas_vindas",
        language="pt_BR",
        category="MARKETING",
        status="APPROVED",
        components=[
            {"type": "HEADER", "format": "TEXT", "text": "Olá, {{1}}!"},
            {"type": "BODY", "text": "Bem-vindo à Atlas Studio. Estamos felizes em ter você conosco."},
            {"type": "FOOTER", "text": "Atlas Studio"},
        ],
    ),
    MockTemplate(
        external_id="mock_followup_proposta",
        name="followup_proposta",
        language="pt_BR",
        category="UTILITY",
        status="APPROVED",
        components=[
            {"type": "BODY", "text": "Olá {{1}}, tudo bem? Gostaria de saber se você teve a oportunidade de analisar nossa proposta."},
        ],
    ),
    MockTemplate(
        external_id="mock_lembrete_reuniao",
        name="lembrete_reuniao",
        language="pt_BR",
        category="UTILITY",
        status="APPROVED",
        components=[
            {"type": "BODY", "text": "Olá {{1}}! Lembrando sobre nossa reunião amanhã às {{2}}. Confirma sua presença?"},
        ],
    ),
]


class MockMessagingProvider:
    """Fully offline messaging provider for development and testing."""

    def send_text(self, to_phone: str, body: str) -> SendTextResult:
        mock_id = f"mock_{uuid.uuid4().hex[:12]}"
        return SendTextResult(provider_message_id=mock_id, success=True)

    def send_template(self, to_phone: str, template_name: str, language: str, components: list[TemplateComponent]) -> SendTextResult:
        mock_id = f"mock_{uuid.uuid4().hex[:12]}"
        return SendTextResult(provider_message_id=mock_id, success=True)

    def get_templates(self) -> list[MockTemplate]:
        return MOCK_TEMPLATES

    def test_connection(self) -> bool:
        return True

    def provider_name(self) -> str:
        return "Mock (Simulação)"
