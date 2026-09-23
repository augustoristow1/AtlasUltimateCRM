"""Tests for HMAC X-Hub-Signature-256 validation on the webhook endpoint."""
import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from atlas_ultimate_crm.webhook.routes import create_router
from fastapi import FastAPI


APP_SECRET = "test_secret_abc123"

SAMPLE_PAYLOAD = {
    "entry": [{
        "id": "123",
        "changes": [{
            "field": "messages",
            "value": {
                "messages": [{
                    "id": "wamid.test001",
                    "from": "5511999990001",
                    "timestamp": "1700000000",
                    "type": "text",
                    "text": {"body": "Oi"},
                }]
            },
        }],
    }]
}


def _sign(body: bytes, secret: str) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


class _FakeSettings:
    meta_app_secret = APP_SECRET
    meta_webhook_verify_token = "token"


class _FakeSettingsNoSecret:
    meta_app_secret = ""
    meta_webhook_verify_token = "token"


class _FakeBootstrap:
    workspace_id = "ws-test"
    settings = _FakeSettings()

    def session_context(self):
        from contextlib import contextmanager

        @contextmanager
        def _ctx():
            class _FakeSession:
                def add(self, obj): pass
                def commit(self): pass
                def get(self, model, eid): return None
            yield _FakeSession()

        return _ctx()

    @property
    def contact_service(self):
        class _CS:
            def get_or_create_by_phone(self, ws_id, phone):
                class _C:
                    id = "c-test"
                return _C()
        return _CS()

    @property
    def messaging_service(self):
        class _MS:
            def handle_inbound(self, **kw): pass
        return _MS()

    @property
    def campaign_service(self):
        class _CS:
            def mark_replied(self, mid): pass
        return _CS()


def _make_client(bootstrap) -> TestClient:
    app = FastAPI()
    app.include_router(create_router(bootstrap))
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def client():
    return _make_client(_FakeBootstrap())


@pytest.fixture()
def client_no_secret():
    bs = _FakeBootstrap()
    bs.settings = _FakeSettingsNoSecret()
    return _make_client(bs)


def _post(client, payload_dict, headers=None):
    body = json.dumps(payload_dict).encode()
    h = {"Content-Type": "application/json"}
    if headers:
        h.update(headers)
    return client.post("/webhook", content=body, headers=h)


# --------------------------------------------------------------------------- #
# Valid signature
# --------------------------------------------------------------------------- #

def test_valid_signature_accepted(client):
    body = json.dumps(SAMPLE_PAYLOAD).encode()
    sig = _sign(body, APP_SECRET)
    resp = client.post(
        "/webhook",
        content=body,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig},
    )
    assert resp.status_code == 200


# --------------------------------------------------------------------------- #
# Invalid signature
# --------------------------------------------------------------------------- #

def test_invalid_signature_rejected(client):
    body = json.dumps(SAMPLE_PAYLOAD).encode()
    resp = client.post(
        "/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=badhash",
        },
    )
    assert resp.status_code == 401


# --------------------------------------------------------------------------- #
# Absent signature header
# --------------------------------------------------------------------------- #

def test_missing_signature_rejected(client):
    body = json.dumps(SAMPLE_PAYLOAD).encode()
    resp = client.post(
        "/webhook",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 401


# --------------------------------------------------------------------------- #
# Tampered payload (signature valid for original body, body modified)
# --------------------------------------------------------------------------- #

def test_tampered_payload_rejected(client):
    original_body = json.dumps(SAMPLE_PAYLOAD).encode()
    sig = _sign(original_body, APP_SECRET)

    tampered = SAMPLE_PAYLOAD.copy()
    tampered["entry"][0]["id"] = "hacked"
    tampered_body = json.dumps(tampered).encode()

    resp = client.post(
        "/webhook",
        content=tampered_body,
        headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig},
    )
    assert resp.status_code == 401


# --------------------------------------------------------------------------- #
# Secret not configured → skip validation (mock mode)
# --------------------------------------------------------------------------- #

def test_no_secret_skips_validation(client_no_secret):
    """When META_APP_SECRET is empty the endpoint accepts any request (mock mode)."""
    body = json.dumps(SAMPLE_PAYLOAD).encode()
    resp = client_no_secret.post(
        "/webhook",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert resp.status_code == 200
