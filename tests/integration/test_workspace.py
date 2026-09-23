import pytest


def test_default_workspace_created(bootstrap):
    assert bootstrap.workspace_id != ""


def test_workspace_persists(bootstrap):
    from atlas_ultimate_crm.infrastructure.database.models.workspace import WorkspaceModel
    from sqlalchemy import select
    with bootstrap.session_context() as session:
        ws = session.scalars(select(WorkspaceModel)).first()
    assert ws is not None
    assert ws.name == "Atlas Studio"
