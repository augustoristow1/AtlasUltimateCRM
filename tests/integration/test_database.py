import pytest
from atlas_ultimate_crm.infrastructure.database.engine import build_engine
from atlas_ultimate_crm.infrastructure.database.base import Base
import atlas_ultimate_crm.infrastructure.database.models  # noqa


def test_create_tables():
    engine = build_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "workspaces" in tables
    assert "contacts" in tables
    assert "conversations" in tables
    assert "deals" in tables
    assert "campaigns" in tables
