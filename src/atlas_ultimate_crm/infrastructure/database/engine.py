from sqlalchemy import Engine, create_engine, event
from sqlalchemy.pool import StaticPool

from atlas_ultimate_crm.core.paths import get_database_path


def build_engine(url: str = "") -> Engine:
    if not url:
        db_path = get_database_path()
        url = f"sqlite:///{db_path}"

    connect_args = {}
    kwargs: dict = {}

    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False, "timeout": 30}
        if url == "sqlite:///:memory:":
            kwargs["connect_args"] = connect_args
            kwargs["poolclass"] = StaticPool
        else:
            kwargs["connect_args"] = connect_args

    engine = create_engine(url, **kwargs)

    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()

    return engine
