"""Tests for campaign reply correlation via mark_replied and webhook context.id."""
import pytest

from atlas_ultimate_crm.bootstrap import Bootstrap
from atlas_ultimate_crm.domain.enums.campaigns import RecipientStatus
from atlas_ultimate_crm.infrastructure.database.repositories.campaign_repository import SQLCampaignRepository
from atlas_ultimate_crm.infrastructure.messaging.whatsapp.parser import parse_webhook_payload


@pytest.fixture()
def bootstrap():
    bs = Bootstrap(database_url="sqlite:///:memory:")
    bs.initialize()
    return bs


def _get_recipients(bootstrap, campaign_id):
    with bootstrap.session_context() as session:
        return SQLCampaignRepository(session).get_recipients(campaign_id)


def _create_sent_campaign(bootstrap):
    ws = bootstrap.workspace_id
    contact = bootstrap.contact_service.create_contact(ws, "Test Contact", phone="+5511777770001")
    campaign = bootstrap.campaign_service.create_campaign(ws, "Test Campaign")
    bootstrap.campaign_service.add_recipients(campaign.id, [contact.id])
    bootstrap.campaign_service.run_campaign(campaign.id, ws)
    return campaign, contact


# ------------------------------------------------------------------ tests

def test_mark_replied_with_context_id(bootstrap):
    """Directly calling mark_replied with the outbound provider_message_id marks the recipient."""
    campaign, contact = _create_sent_campaign(bootstrap)

    recipients = _get_recipients(bootstrap, campaign.id)
    sent = next((r for r in recipients if r.provider_message_id), None)
    if not sent:
        pytest.skip("Mock provider did not produce a provider_message_id")

    bootstrap.campaign_service.mark_replied(sent.provider_message_id)

    updated = _get_recipients(bootstrap, campaign.id)
    replied = [r for r in updated if r.status == RecipientStatus.REPLIED]
    assert len(replied) == 1
    assert replied[0].replied_at is not None


def test_mark_replied_no_matching_id_is_noop(bootstrap):
    """mark_replied with an unknown ID does not crash and changes nothing."""
    campaign, _ = _create_sent_campaign(bootstrap)
    before = _get_recipients(bootstrap, campaign.id)

    bootstrap.campaign_service.mark_replied("wamid.doesnotexist")

    after = _get_recipients(bootstrap, campaign.id)
    # Status should be unchanged
    for b, a in zip(before, after):
        assert b.status == a.status


def test_mark_replied_duplicate_is_idempotent(bootstrap):
    """Calling mark_replied twice with the same ID does not raise or double-count."""
    campaign, _ = _create_sent_campaign(bootstrap)
    recipients = _get_recipients(bootstrap, campaign.id)
    sent = next((r for r in recipients if r.provider_message_id), None)
    if not sent:
        pytest.skip("Mock provider did not produce a provider_message_id")

    bootstrap.campaign_service.mark_replied(sent.provider_message_id)
    bootstrap.campaign_service.mark_replied(sent.provider_message_id)  # duplicate

    updated = _get_recipients(bootstrap, campaign.id)
    replied = [r for r in updated if r.status == RecipientStatus.REPLIED]
    assert len(replied) == 1  # still only one


def test_parser_extracts_context_id():
    """Parser extracts context.id from a reply message payload."""
    payload = {
        "entry": [{
            "id": "123",
            "changes": [{
                "field": "messages",
                "value": {
                    "messages": [{
                        "id": "wamid.reply001",
                        "from": "5511999990001",
                        "timestamp": "1700000010",
                        "type": "text",
                        "text": {"body": "Sim, tenho interesse!"},
                        "context": {"id": "wamid.original001"},
                    }]
                },
            }],
        }]
    }
    events = parse_webhook_payload(payload)
    assert len(events) == 1
    assert events[0]["context_id"] == "wamid.original001"


def test_parser_context_id_absent_when_no_reply():
    """Parser returns empty context_id when no context is present."""
    payload = {
        "entry": [{
            "id": "123",
            "changes": [{
                "field": "messages",
                "value": {
                    "messages": [{
                        "id": "wamid.newmsg001",
                        "from": "5511999990002",
                        "timestamp": "1700000020",
                        "type": "text",
                        "text": {"body": "Olá"},
                    }]
                },
            }],
        }]
    }
    events = parse_webhook_payload(payload)
    assert events[0]["context_id"] == ""
