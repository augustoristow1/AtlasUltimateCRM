import logging
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query, Request, Response

from atlas_ultimate_crm.webhook.verification import verify_whatsapp_signature

logger = logging.getLogger(__name__)


def create_router(bootstrap) -> APIRouter:
    router = APIRouter()

    @router.get("/webhook")
    async def verify_webhook(
        hub_mode: str = Query(alias="hub.mode", default=""),
        hub_challenge: str = Query(alias="hub.challenge", default=""),
        hub_verify_token: str = Query(alias="hub.verify_token", default=""),
    ):
        expected_token = bootstrap.settings.meta_webhook_verify_token
        if hub_mode == "subscribe" and hub_verify_token == expected_token:
            return Response(content=hub_challenge, media_type="text/plain")
        raise HTTPException(status_code=403, detail="Verification failed")

    @router.post("/webhook")
    async def receive_webhook(request: Request):
        body = await request.body()

        app_secret = bootstrap.settings.meta_app_secret
        if app_secret:
            signature = request.headers.get("X-Hub-Signature-256", "")
            if not signature:
                raise HTTPException(status_code=401, detail="Missing X-Hub-Signature-256")
            if not verify_whatsapp_signature(body, signature, app_secret):
                raise HTTPException(status_code=401, detail="Invalid signature")

        payload = await request.json()

        # Persist webhook event
        event_id = str(uuid.uuid4())
        with bootstrap.session_context() as session:
            import json

            from atlas_ultimate_crm.infrastructure.database.models.system import WebhookEventModel
            event = WebhookEventModel(
                id=event_id,
                workspace_id=bootstrap.workspace_id,
                event_type="whatsapp",
                payload_json=json.dumps(payload),
                received_at=datetime.now(UTC),
                status="received",
            )
            session.add(event)
            session.commit()

        # Parse and dispatch
        try:
            from atlas_ultimate_crm.infrastructure.messaging.whatsapp.parser import (
                parse_webhook_payload,
            )
            events = parse_webhook_payload(payload)
            for evt in events:
                await _handle_event(evt, bootstrap)

            with bootstrap.session_context() as session:
                from atlas_ultimate_crm.infrastructure.database.models.system import (
                    WebhookEventModel,
                )
                m = session.get(WebhookEventModel, event_id)
                if m:
                    m.status = "processed"
                    m.processed_at = datetime.now(UTC)
                    session.commit()
        except Exception as e:
            logger.error("Webhook processing error: %s", e)

        return {"status": "ok"}

    return router


async def _handle_event(event: dict, bootstrap) -> None:
    event_type = event.get("type")
    if event_type == "message_received":
        phone = event.get("from_phone", "")
        body = event.get("body", "")
        provider_message_id = event.get("message_id", "")
        ws_id = bootstrap.workspace_id

        contact = bootstrap.contact_service.get_or_create_by_phone(ws_id, phone)
        bootstrap.messaging_service.handle_inbound(
            workspace_id=ws_id,
            contact_id=contact.id,
            phone=phone,
            body=body,
            provider_message_id=provider_message_id,
        )
        # Campaign reply correlation:
        # Prefer context.id (the original message being replied to) for direct correlation.
        # Fall back to the inbound message_id if context is absent (e.g. first reply without quote).
        context_id = event.get("context_id", "")
        reply_correlation_id = context_id or provider_message_id
        if reply_correlation_id:
            bootstrap.campaign_service.mark_replied(reply_correlation_id)

    elif event_type == "message_status":
        provider_message_id = event.get("message_id", "")
        status = event.get("status", "")
        failure_reason = event.get("failure_reason", "")
        logger.info("Message status update: %s -> %s", provider_message_id, status)
        if provider_message_id and status:
            _update_message_status(bootstrap, provider_message_id, status, failure_reason)


# Status priority: higher index = more advanced (no regression allowed)
_STATUS_ORDER = ["queued", "sent", "delivered", "read", "failed"]


def _update_message_status(
    bootstrap, provider_message_id: str, status: str, failure_reason: str
) -> None:
    from sqlalchemy import select

    from atlas_ultimate_crm.infrastructure.database.models.conversations import MessageModel

    now = datetime.now(UTC)
    with bootstrap.session_context() as session:
        msg = session.scalars(
            select(MessageModel).where(MessageModel.provider_message_id == provider_message_id)
        ).first()
        if msg is None:
            logger.debug("No message found for provider_message_id=%s", provider_message_id)
            return

        current_order = _STATUS_ORDER.index(msg.status) if msg.status in _STATUS_ORDER else -1
        new_order = _STATUS_ORDER.index(status) if status in _STATUS_ORDER else -1

        # Never regress status (e.g. read → delivered is rejected)
        # Exception: failed can always be set
        if status != "failed" and new_order <= current_order:
            logger.debug(
                "Ignoring status regression %s -> %s for %s",
                msg.status, status, provider_message_id,
            )
            return

        msg.status = status
        if status == "sent" and msg.sent_at is None:
            msg.sent_at = now
        elif status == "delivered" and msg.delivered_at is None:
            msg.delivered_at = now
        elif status == "read" and msg.read_at is None:
            msg.read_at = now
        elif status == "failed":
            msg.failed_at = now
            if failure_reason:
                msg.failure_reason = failure_reason

        try:
            session.commit()
        except Exception:
            session.rollback()
            raise
