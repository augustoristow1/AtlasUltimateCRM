from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppMode(str, Enum):
    MOCK = "mock"
    META = "meta"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_mode: AppMode = AppMode.MOCK
    log_level: str = "INFO"
    database_url: str = ""

    meta_graph_api_version: str = "v19.0"
    meta_access_token: str = ""
    meta_waba_id: str = ""
    meta_phone_number_id: str = ""
    meta_app_secret: str = ""
    meta_webhook_verify_token: str = "atlas_webhook_token"


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
