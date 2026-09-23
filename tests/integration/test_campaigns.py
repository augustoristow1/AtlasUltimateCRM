from atlas_ultimate_crm.domain.enums.campaigns import CampaignStatus, RecipientStatus
from atlas_ultimate_crm.infrastructure.database.repositories.campaign_repository import SQLCampaignRepository


def _get_recipients(bootstrap, campaign_id):
    with bootstrap.session_context() as session:
        return SQLCampaignRepository(session).get_recipients(campaign_id)


def test_create_campaign(bootstrap):
    campaign = bootstrap.campaign_service.create_campaign(
        workspace_id=bootstrap.workspace_id,
        name="Campanha Teste",
    )
    assert campaign.id != ""
    assert campaign.status == CampaignStatus.DRAFT


def test_run_campaign_mock(bootstrap):
    ws = bootstrap.workspace_id
    contact = bootstrap.contact_service.create_contact(ws, "Camp Contact", phone="+5511888888888")
    campaign = bootstrap.campaign_service.create_campaign(ws, "Campanha Mock")
    bootstrap.campaign_service.add_recipients(campaign.id, [contact.id])
    bootstrap.campaign_service.run_campaign(campaign.id, ws)

    recipients = _get_recipients(bootstrap, campaign.id)
    assert len(recipients) == 1
    assert recipients[0].status in (RecipientStatus.SENT, RecipientStatus.SKIPPED)


def test_campaign_reply(bootstrap):
    ws = bootstrap.workspace_id
    contact = bootstrap.contact_service.create_contact(ws, "Reply Contact", phone="+5511000000001")
    campaign = bootstrap.campaign_service.create_campaign(ws, "Reply Campaign")
    bootstrap.campaign_service.add_recipients(campaign.id, [contact.id])
    bootstrap.campaign_service.run_campaign(campaign.id, ws)

    recipients = _get_recipients(bootstrap, campaign.id)
    sent_recipient = next((r for r in recipients if r.provider_message_id), None)
    if sent_recipient and sent_recipient.provider_message_id:
        bootstrap.campaign_service.mark_replied(sent_recipient.provider_message_id)
        updated = _get_recipients(bootstrap, campaign.id)
        replied = [r for r in updated if r.status == RecipientStatus.REPLIED]
        assert len(replied) >= 1
