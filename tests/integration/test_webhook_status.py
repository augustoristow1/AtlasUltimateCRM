"""Tests for message status persistence via webhook status events."""
import json
import uuid
from datetime import datetime, UTC

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.pool import StaticPool
from sqlalchemy import event as sa_event

from atlas_ultimate_crm.infrastructure.database.base import Base
from atlas_ultimate_crm.infrastructure.database.session import SessionFactory
from atlas_ultimate_crm.infrastructure.database.models.conversations import MessageModel
import atlas_ultimate_crm.infrastructure.database.models  # noqa

from atlas_ultimate_crm.webhook.routes import _update_message_status, _STATUS_ORDER


# ------------------------------------------------------------------ fixtures


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @sa_event.listens_for(eng, "connect")
    def set_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=OFF")  # OFF so we can insert messages without FK
        cursor.close()

    Base.metadata.create_all(eng)
    return eng


@pytest.fixture()
def session_factory(engine):
    return SessionFactory(engine)


def _make_message(session_factory, status: str = "sent", provider_id: str = "") -> str:
    """Insert a MessageModel and return its provider_message_id."""
    provider_id = provider_id or f"wamid.{uuid.uuid4().hex}"
    msg_id = str(uuid.uuid4())
    with session_factory() as s:
        m = MessageModel(
            id=msg_id,
            workspace_id="ws1",
            conversation_id="conv1",
            contact_id="c1",
            provider_message_id=provider_id,
            direction="outbound",
            status=status,
        )
        s.add(m)
        s.commit()
    return provider_id


class _FakeBootstrap:
    def __init__(self, session_factory):
        self._sf = session_factory

    def session_context(self):
        return self._sf()


def _get_msg(session_factory, provider_id: str):
    with session_factory() as s:
        return s.scalars(
            select(MessageModel).where(MessageModel.provider_message_id == provider_id)
        ).first()


# ------------------------------------------------------------------ tests


def test_sent_updates_sent_at(session_factory):
    bs = _FakeBootstrap(session_factory)
    pid = _make_message(session_factory, status="queued")

    _update_message_status(bs, pid, "sent", "")

    msg = _get_msg(session_factory, pid)
    assert msg.status == "sent"
    assert msg.sent_at is not None


def test_delivered_updates_delivered_at(session_factory):
    bs = _FakeBootstrap(session_factory)
    pid = _make_message(session_factory, status="sent")
    _update_message_status(bs, pid, "delivered", "")

    msg = _get_msg(session_factory, pid)
    assert msg.status == "delivered"
    assert msg.delivered_at is not None


def test_read_updates_read_at(session_factory):
    bs = _FakeBootstrap(session_factory)
    pid = _make_message(session_factory, status="delivered")
    _update_message_status(bs, pid, "read", "")

    msg = _get_msg(session_factory, pid)
    assert msg.status == "read"
    assert msg.read_at is not None


def test_failed_updates_failed_at_and_reason(session_factory):
    bs = _FakeBootstrap(session_factory)
    pid = _make_message(session_factory, status="sent")
    _update_message_status(bs, pid, "failed", "Recipient not reachable")

    msg = _get_msg(session_factory, pid)
    assert msg.status == "failed"
    assert msg.failed_at is not None
    assert msg.failure_reason == "Recipient not reachable"


def test_no_status_regression_read_to_delivered(session_factory):
    bs = _FakeBootstrap(session_factory)
    pid = _make_message(session_factory, status="read")

    _update_message_status(bs, pid, "delivered", "")

    msg = _get_msg(session_factory, pid)
    assert msg.status == "read"  # must not regress


def test_no_status_regression_delivered_to_sent(session_factory):
    bs = _FakeBootstrap(session_factory)
    pid = _make_message(session_factory, status="delivered")

    _update_message_status(bs, pid, "sent", "")

    msg = _get_msg(session_factory, pid)
    assert msg.status == "delivered"


def test_duplicate_sent_event_idempotent(session_factory):
    bs = _FakeBootstrap(session_factory)
    pid = _make_message(session_factory, status="queued")

    _update_message_status(bs, pid, "sent", "")
    first_sent_at = _get_msg(session_factory, pid).sent_at

    _update_message_status(bs, pid, "sent", "")  # duplicate
    msg = _get_msg(session_factory, pid)
    assert msg.sent_at == first_sent_at  # unchanged


def test_unknown_provider_id_is_noop(session_factory):
    bs = _FakeBootstrap(session_factory)
    # Should not raise, just log a debug message
    _update_message_status(bs, "wamid.doesnotexist", "delivered", "")
