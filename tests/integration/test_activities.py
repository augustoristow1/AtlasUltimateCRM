from atlas_ultimate_crm.domain.enums.activities import ActivityType


def test_activity_created_on_contact(bootstrap):
    ws = bootstrap.workspace_id
    contact = bootstrap.contact_service.create_contact(ws, "Activity Contact", phone="+5511000000002")
    activities = bootstrap.activity_service.list_for_contact(contact.id)
    types = [a.activity_type for a in activities]
    assert ActivityType.CONTACT_CREATED in types


def test_record_activity(bootstrap):
    ws = bootstrap.workspace_id
    contact = bootstrap.contact_service.create_contact(ws, "Manual Activity", phone="+5511000000003")
    bootstrap.activity_service.record(
        ws, ActivityType.NOTE_CREATED, contact_id=contact.id, metadata={"note": "test"}
    )
    activities = bootstrap.activity_service.list_for_contact(contact.id)
    assert any(a.activity_type == ActivityType.NOTE_CREATED for a in activities)
