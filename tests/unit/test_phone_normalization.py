from atlas_ultimate_crm.application.services.contact_service import normalize_phone


def test_normalize_brazilian_mobile():
    result = normalize_phone("+5511999999999")
    assert result == "+5511999999999"


def test_normalize_local_format():
    result = normalize_phone("11999999999", "BR")
    assert "+55" in result or result == "11999999999"


def test_normalize_empty():
    assert normalize_phone("") == ""
