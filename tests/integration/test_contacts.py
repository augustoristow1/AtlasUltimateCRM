import pytest
from atlas_ultimate_crm.domain.enums.contact import ContactSource


def test_create_contact(bootstrap):
    contact = bootstrap.contact_service.create_contact(
        workspace_id=bootstrap.workspace_id,
        name="João Silva",
        phone="+5511999999999",
        email="joao@example.com",
    )
    assert contact.id != ""
    assert contact.name == "João Silva"


def test_contact_dedup_by_phone(bootstrap):
    ws = bootstrap.workspace_id
    c1 = bootstrap.contact_service.create_contact(ws, "Ana", phone="+5511988887777")
    c2 = bootstrap.contact_service.create_contact(ws, "Ana Duplicada", phone="+5511988887777")
    assert c1.id == c2.id


def test_list_contacts(bootstrap):
    ws = bootstrap.workspace_id
    bootstrap.contact_service.create_contact(ws, "Contato A", phone="+5511111111111")
    bootstrap.contact_service.create_contact(ws, "Contato B", phone="+5511222222222")
    contacts = bootstrap.contact_service.list_contacts(ws)
    assert len(contacts) >= 2


def test_count_contacts(bootstrap):
    ws = bootstrap.workspace_id
    before = bootstrap.contact_service.count_contacts(ws)
    bootstrap.contact_service.create_contact(ws, "Test Count", phone="+5511333333333")
    after = bootstrap.contact_service.count_contacts(ws)
    assert after == before + 1
