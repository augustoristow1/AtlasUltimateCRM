"""
Secrets storage abstraction.
Currently uses environment variables.
Future: macOS Keychain via keyring library.
"""
import os


class SecretsStore:
    """Abstract secrets storage - env vars now, Keychain later."""

    def get(self, key: str, default: str = "") -> str:
        return os.environ.get(key, default)

    def set(self, key: str, value: str) -> None:
        # Future: store in macOS Keychain
        os.environ[key] = value
