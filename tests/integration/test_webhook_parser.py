from atlas_ultimate_crm.infrastructure.messaging.whatsapp.parser import parse_webhook_payload


def test_parse_inbound_message():
    payload = {
        "entry": [{
            "id": "123",
            "changes": [{
                "field": "messages",
                "value": {
                    "messages": [{
                        "id": "wamid.001",
                        "from": "5511999990001",
                        "timestamp": "1700000000",
                        "type": "text",
                        "text": {"body": "Olá!"}
                    }]
                }
            }]
        }]
    }
    events = parse_webhook_payload(payload)
    assert len(events) == 1
    assert events[0]["type"] == "message_received"
    assert events[0]["body"] == "Olá!"
    assert events[0]["from_phone"] == "5511999990001"


def test_parse_status_update():
    payload = {
        "entry": [{
            "id": "123",
            "changes": [{
                "field": "messages",
                "value": {
                    "statuses": [{
                        "id": "wamid.002",
                        "status": "delivered",
                        "timestamp": "1700000001",
                        "recipient_id": "5511999990001"
                    }]
                }
            }]
        }]
    }
    events = parse_webhook_payload(payload)
    assert len(events) == 1
    assert events[0]["type"] == "message_status"
    assert events[0]["status"] == "delivered"


def test_parse_messaging_policy():
    from datetime import datetime, UTC, timedelta
    from atlas_ultimate_crm.application.services.messaging_policy_service import MessagingPolicyService
    from atlas_ultimate_crm.domain.entities.conversation import ConversationEntity
    from atlas_ultimate_crm.domain.enums.messaging import ChannelType

    conv = ConversationEntity(
        workspace_id="ws1", contact_id="c1", channel=ChannelType.WHATSAPP,
        service_window_expires_at=datetime.now(UTC) + timedelta(hours=12)
    )

    class MockSession:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def scalars(self, *a):
            class R:
                def first(self): return None
            return R()

    class MockFactory:
        def __call__(self): return MockSession()

    svc = MessagingPolicyService(MockFactory())
    assert svc.can_send_freeform(conv) is True
    assert svc.requires_template(conv) is False
