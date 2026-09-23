def test_send_text_mock(bootstrap):
    ws = bootstrap.workspace_id
    contact = bootstrap.contact_service.create_contact(ws, "Msg Contact", phone="+5511555555555")
    result = bootstrap.messaging_service.send_text_to_contact(
        ws, contact.id, contact.phone, "Olá!"
    )
    assert result is True


def test_handle_inbound(bootstrap):
    ws = bootstrap.workspace_id
    contact = bootstrap.contact_service.create_contact(ws, "Inbound Contact", phone="+5511666666666")
    bootstrap.messaging_service.handle_inbound(
        workspace_id=ws,
        contact_id=contact.id,
        phone=contact.phone,
        body="Resposta do cliente",
        provider_message_id="sim_test_001",
    )
    messages = bootstrap.conversation_service.list_messages(
        bootstrap.conversation_service.get_or_create_conversation(ws, contact.id).id
    )
    inbound = [m for m in messages if m.direction.value == "inbound"]
    assert len(inbound) >= 1


def test_conversation_created(bootstrap):
    ws = bootstrap.workspace_id
    contact = bootstrap.contact_service.create_contact(ws, "Conv Contact", phone="+5511777777777")
    conv = bootstrap.conversation_service.get_or_create_conversation(ws, contact.id)
    assert conv.id != ""
    same_conv = bootstrap.conversation_service.get_or_create_conversation(ws, contact.id)
    assert same_conv.id == conv.id
