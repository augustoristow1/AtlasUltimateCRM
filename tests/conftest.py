import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from atlas_ultimate_crm.infrastructure.database.base import Base
from atlas_ultimate_crm.infrastructure.database.session import SessionFactory
import atlas_ultimate_crm.infrastructure.database.models  # noqa


@pytest.fixture(scope="function")
def engine():
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    from sqlalchemy import event
    @event.listens_for(eng, "connect")
    def set_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture(scope="function")
def session_factory(engine):
    return SessionFactory(engine)


@pytest.fixture(scope="function")
def bootstrap(engine):
    from atlas_ultimate_crm.bootstrap import Bootstrap
    bs = Bootstrap(database_url="sqlite:///:memory:")
    bs.engine = engine
    bs._session_factory_raw = SessionFactory(engine)
    bs._build_services()
    bs._ensure_default_workspace()
    bs._ensure_default_pipeline()
    return bs
