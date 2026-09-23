import hashlib
import hmac


def verify_whatsapp_signature(payload: bytes, signature: str, app_secret: str) -> bool:
    """Verify X-Hub-Signature-256 from Meta."""
    expected = "sha256=" + hmac.new(app_secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
