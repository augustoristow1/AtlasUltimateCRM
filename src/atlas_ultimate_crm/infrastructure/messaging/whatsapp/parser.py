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
                    events.append({
                        "type": "message_received",
                        "message_id": msg.get("id", ""),
                        "from_phone": msg.get("from", ""),
                        "timestamp": msg.get("timestamp", ""),
                        "message_type": msg.get("type", "text"),
                        "body": msg.get("text", {}).get("body", "") if msg.get("type") == "text" else "",
                        "raw": msg,
                    })

                for status in value.get("statuses", []):
                    events.append({
                        "type": "message_status",
                        "message_id": status.get("id", ""),
                        "status": status.get("status", ""),
                        "timestamp": status.get("timestamp", ""),
                        "recipient_id": status.get("recipient_id", ""),
                    })

    return events
