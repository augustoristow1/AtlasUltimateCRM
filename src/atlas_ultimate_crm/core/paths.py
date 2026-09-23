from pathlib import Path


APP_NAME = "Atlas Ultimate CRM"


def get_app_support_dir() -> Path:
    base = Path.home() / "Library" / "Application Support" / APP_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_database_path() -> Path:
    return get_app_support_dir() / "atlas_ultimate.db"


def get_logs_dir() -> Path:
    logs = get_app_support_dir() / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    return logs
