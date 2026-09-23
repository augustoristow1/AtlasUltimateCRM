def test_default_pipeline_created(bootstrap):
    ws = bootstrap.workspace_id
    pipeline, stages = bootstrap.pipeline_service.get_or_create_default_pipeline(ws)
    assert pipeline is not None
    assert len(stages) == 7
    assert stages[0].name == "Novo"
    assert stages[-1].name == "Perdido"


def test_create_deal(bootstrap):
    ws = bootstrap.workspace_id
    pipeline, stages = bootstrap.pipeline_service.get_or_create_default_pipeline(ws)
    contact = bootstrap.contact_service.create_contact(ws, "Deal Contact", phone="+5511444444444")
    deal = bootstrap.deal_service.create_deal(
        workspace_id=ws,
        pipeline_id=pipeline.id,
        stage_id=stages[0].id,
        title="Venda Teste",
        contact_id=contact.id,
        value=5000.0,
    )
    assert deal.id != ""
    assert deal.title == "Venda Teste"


def test_change_deal_stage(bootstrap):
    ws = bootstrap.workspace_id
    pipeline, stages = bootstrap.pipeline_service.get_or_create_default_pipeline(ws)
    deal = bootstrap.deal_service.create_deal(
        workspace_id=ws, pipeline_id=pipeline.id,
        stage_id=stages[0].id, title="Test Stage Change",
    )
    updated = bootstrap.deal_service.change_stage(deal.id, stages[1].id)
    assert updated.stage_id == stages[1].id
