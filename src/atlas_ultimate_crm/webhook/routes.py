import logging
import uuid
from datetime import datetime, UTC
from fastapi import APIRouter, Request, Response, HTTPException, Query

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
        payload = await request.json()

        # Persist webhook event
        event_id = str(uuid.uuid4())
        with bootstrap.session_context() as session:
            from atlas_ultimate_crm.infrastructure.database.models.system import WebhookEventModel
            import json
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
            from atlas_ultimate_crm.infrastructure.messaging.whatsapp.parser import parse_webhook_payload
            events = parse_webhook_payload(payload)
            for evt in events:
                await _handle_event(evt, bootstrap)

            with bootstrap.session_context() as session:
                from atlas_ultimate_crm.infrastructure.database.models.system import WebhookEventModel
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
        # Check campaign reply
        if provider_message_id:
            bootstrap.campaign_service.mark_replied(provider_message_id)

    elif event_type == "message_status":
        provider_message_id = event.get("message_id", "")
        status = event.get("status", "")
        logger.info("Message status update: %s -> %s", provider_message_id, status)
