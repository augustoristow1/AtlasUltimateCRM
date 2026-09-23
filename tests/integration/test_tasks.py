from atlas_ultimate_crm.domain.enums.tasks import TaskStatus


def test_create_task(bootstrap):
    ws = bootstrap.workspace_id
    task = bootstrap.task_service.create_task(ws, "Ligar para cliente")
    assert task.id != ""
    assert task.status == TaskStatus.PENDING


def test_complete_task(bootstrap):
    ws = bootstrap.workspace_id
    task = bootstrap.task_service.create_task(ws, "Tarefa a concluir")
    completed = bootstrap.task_service.complete_task(task.id)
    assert completed.status == TaskStatus.COMPLETED


def test_count_pending(bootstrap):
    ws = bootstrap.workspace_id
    before = bootstrap.task_service.count_pending(ws)
    bootstrap.task_service.create_task(ws, "Nova tarefa")
    after = bootstrap.task_service.count_pending(ws)
    assert after == before + 1
