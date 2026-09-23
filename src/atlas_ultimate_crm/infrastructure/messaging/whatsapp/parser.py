import logging
from typing import Any

logger = logging.getLogger(__name__)


def parse_webhook_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse WhatsApp Cloud API webhook payload into normalized internal events."""
    events = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            event_type = change.get("field", "")

            if event_type == "messages":
                for msg in value.get("messages", []):
                    # context.id is present when this message is a reply to a previous message
                    context_id = msg.get("context", {}).get("id", "")
                    events.append({
                        "type": "message_received",
                        "message_id": msg.get("id", ""),
                        "from_phone": msg.get("from", ""),
                        "timestamp": msg.get("timestamp", ""),
                        "message_type": msg.get("type", "text"),
                        "body": msg.get("text", {}).get("body", "") if msg.get("type") == "text" else "",
                        "context_id": context_id,  # ID of the original message being replied to
                        "raw": msg,
                    })

                for status in value.get("statuses", []):
                    errors = status.get("errors", [])
                    failure_reason = errors[0].get("message", "") if errors else ""
                    events.append({
                        "type": "message_status",
                        "message_id": status.get("id", ""),
                        "status": status.get("status", ""),
                        "timestamp": status.get("timestamp", ""),
                        "recipient_id": status.get("recipient_id", ""),
                        "failure_reason": failure_reason,
                    })

    return events
