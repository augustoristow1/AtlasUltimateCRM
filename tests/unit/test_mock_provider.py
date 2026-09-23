from atlas_ultimate_crm.infrastructure.messaging.mock.provider import MockMessagingProvider


def test_send_text():
    provider = MockMessagingProvider()
    result = provider.send_text("+5511999999999", "Hello")
    assert result.success is True
    assert result.provider_message_id.startswith("mock_")


def test_send_template():
    provider = MockMessagingProvider()
    result = provider.send_template("+5511999999999", "boas_vindas", "pt_BR", [])
    assert result.success is True


def test_get_templates():
    provider = MockMessagingProvider()
    templates = provider.get_templates()
    assert len(templates) >= 3


def test_test_connection():
    provider = MockMessagingProvider()
    assert provider.test_connection() is True


def test_provider_name():
    provider = MockMessagingProvider()
    assert "Mock" in provider.provider_name()
