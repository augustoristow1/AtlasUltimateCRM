"""Tests for inbound message idempotency."""
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.pool import StaticPool
from sqlalchemy import event as sa_event

from atlas_ultimate_crm.infrastructure.database.base import Base
from atlas_ultimate_crm.infrastructure.database.session import SessionFactory
from atlas_ultimate_crm.infrastructure.database.models.conversations import MessageModel
import atlas_ultimate_crm.infrastructure.database.models  # noqa
from atlas_ultimate_crm.bootstrap import Bootstrap


@pytest.fixture()
def bootstrap():
    bs = Bootstrap(database_url="sqlite:///:memory:")
    bs.initialize()
    return bs


def test_duplicate_inbound_message_is_ignored(bootstrap):
    ws_id = bootstrap.workspace_id
    contact = bootstrap.contact_service.get_or_create_by_phone(ws_id, "+5511999990001")
    conv = bootstrap.conversation_service.get_or_create_conversation(ws_id, contact.id)

    provider_id = "wamid.unique001"

    msg1 = bootstrap.conversation_service.save_inbound_message(
        ws_id, conv.id, contact.id, "Olá!", provider_id
    )
    msg2 = bootstrap.conversation_service.save_inbound_message(
        ws_id, conv.id, contact.id, "Olá!", provider_id  # duplicate
    )

    # Both calls succeed and return the same logical message
    assert msg1.id == msg2.id

    # Only one record in the database
    with bootstrap.session_context() as s:
        count = len(s.scalars(
            select(MessageModel).where(MessageModel.provider_message_id == provider_id)
        ).all())
    assert count == 1


def test_different_provider_ids_are_both_saved(bootstrap):
    ws_id = bootstrap.workspace_id
    contact = bootstrap.contact_service.get_or_create_by_phone(ws_id, "+5511999990002")
    conv = bootstrap.conversation_service.get_or_create_conversation(ws_id, contact.id)

    bootstrap.conversation_service.save_inbound_message(
        ws_id, conv.id, contact.id, "Msg 1", "wamid.aaa"
    )
    bootstrap.conversation_service.save_inbound_message(
        ws_id, conv.id, contact.id, "Msg 2", "wamid.bbb"
    )

    with bootstrap.session_context() as s:
        msgs = s.scalars(
            select(MessageModel).where(MessageModel.conversation_id == conv.id)
        ).all()
    assert len(msgs) == 2


def test_empty_provider_id_allows_multiple_messages(bootstrap):
    """Messages with no provider_id (e.g. manual notes) are never deduplicated."""
    ws_id = bootstrap.workspace_id
    contact = bootstrap.contact_service.get_or_create_by_phone(ws_id, "+5511999990003")
    conv = bootstrap.conversation_service.get_or_create_conversation(ws_id, contact.id)

    bootstrap.conversation_service.save_inbound_message(
        ws_id, conv.id, contact.id, "Nota 1", ""
    )
    bootstrap.conversation_service.save_inbound_message(
        ws_id, conv.id, contact.id, "Nota 2", ""
    )

    with bootstrap.session_context() as s:
        msgs = s.scalars(
            select(MessageModel).where(MessageModel.conversation_id == conv.id)
        ).all()
    assert len(msgs) == 2
