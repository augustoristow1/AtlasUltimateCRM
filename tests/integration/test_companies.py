def test_create_company(bootstrap):
    company = bootstrap.company_service.create_company(
        workspace_id=bootstrap.workspace_id,
        name="Acme Corp",
        industry="Tecnologia",
        city="São Paulo",
    )
    assert company.id != ""
    assert company.name == "Acme Corp"


def test_list_companies(bootstrap):
    ws = bootstrap.workspace_id
    bootstrap.company_service.create_company(ws, "Empresa A")
    bootstrap.company_service.create_company(ws, "Empresa B")
    companies = bootstrap.company_service.list_companies(ws)
    assert len(companies) >= 2
