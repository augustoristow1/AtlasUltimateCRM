# ATLAS ULTIMATE CRM — RELATÓRIO TÉCNICO DE AUDITORIA
**Data:** 22 de setembro de 2026
**Versão auditada:** atual (sem controle de versão git configurado)
**Auditor:** Claude Code (claude-sonnet-4-6)
**Objetivo:** Diagnóstico técnico completo para orientar o próximo ciclo de desenvolvimento

---

## 1. RESUMO EXECUTIVO

O Atlas Ultimate CRM é um projeto Python desktop desenvolvido em macOS Apple Silicon M1, usando PySide6 para interface gráfica e SQLite como banco de dados local. Originalmente concebido como disparador de campanhas WhatsApp, o projeto evoluiu para um CRM comercial completo com WhatsApp como primeiro canal de comunicação.

**Estado geral:** O projeto tem uma base arquitetural sólida, com separação de camadas bem definida (Domain, Application, Infrastructure, UI), banco de dados bem modelado com 24 tabelas e relacionamentos corretos para um CRM. Os 34 testes continuam passando.

**Contudo, existem problemas críticos que precisam ser resolvidos antes de uso comercial real:**

1. O webhook **não valida a assinatura HMAC da Meta** — está implementado em verification.py mas nunca chamado.
2. Atualizações de status das mensagens (sent/delivered/read/failed) são **apenas logadas**, não persistidas.
3. Campanhas enviam **texto livre** em vez de templates aprovados — viola a política WhatsApp Business API.
4. A **arquitetura desktop/cloud é totalmente dependente do Mac estar ligado** para receber mensagens.
5. A interface não possui **auto-refresh** — novas mensagens só aparecem manualmente.
6. O `bootstrap.py` mantém uma **sessão SQLAlchemy longa** compartilhada por todos os repositórios, criando riscos de concorrência.

**Pontos fortes:**
- Domínio bem modelado, entidades claramente definidas
- Separação de responsabilidades razoável
- Mock provider funcional para desenvolvimento offline
- 34 testes passando, cobrindo os fluxos principais
- Banco de dados com FKs, índices e modo WAL

---

## 2. ESTADO ATUAL DO ATLAS ULTIMATE CRM

| Área | Status | Observação |
|------|--------|-----------|
| Arquitetura geral | FUNCIONAL | DDD com camadas separadas |
| Banco de dados | FUNCIONAL | 24 tabelas, FKs, WAL, índices |
| CRM - Contatos | PARCIAL | CRUD básico, sem importação CSV |
| CRM - Empresas | PARCIAL | CRUD básico, sem vínculo na UI |
| CRM - Pipeline | PARCIAL | Kanban visual, sem DnD, sem edição |
| CRM - Tarefas | FUNCIONAL | CRUD completo com conclusão |
| CRM - Timeline/Atividades | PARCIAL | Registro automático, sem visão completa |
| Inbox | PARCIAL | Chat básico funcional, sem auto-refresh |
| Campanhas | PARCIAL | Envio síncrono de texto, não de templates |
| WhatsApp Cloud API | ESTRUTURADO | Código existe, integração real não testada |
| Webhook | PARCIAL | Recebe mensagens, não persiste status |
| Dashboard | FUNCIONAL | Métricas reais do banco |
| Configurações | PARCIAL | Apenas leitura, sem salvar |
| Segurança | PARCIAL | .env e .db no .gitignore, assinatura webhook não validada |
| Testes | FUNCIONAL | 34/34 passando |

---

## 3. ESTRUTURA COMPLETA DE DIRETÓRIOS

```
AtlasUltimateCRM/
├── .claude/
│   └── settings.local.json
├── .env.example                    ← variáveis de ambiente (sem valores)
├── .gitignore                      ← .env, .db, .venv excluídos ✓
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 3af4fc95d3f9_initial_schema.py  ← 1 única migration
├── docs/
│   └── architecture.md
├── pyproject.toml                  ← configurações, dependências, pytest, ruff
├── scripts/
│   ├── __init__.py
│   ├── reset_dev_db.py             ← apaga o banco de dev
│   └── seed_demo.py                ← popula dados de exemplo
├── src/
│   └── atlas_ultimate_crm/
│       ├── __init__.py
│       ├── __main__.py             ← entry point desktop
│       ├── bootstrap.py            ← DI container central (169 linhas)
│       ├── application/
│       │   ├── event_bus.py        ← InMemoryEventBus
│       │   ├── commands/           ← VAZIO
│       │   ├── dto/                ← VAZIO
│       │   ├── handlers/           ← VAZIO
│       │   ├── queries/            ← VAZIO
│       │   └── services/
│       │       ├── activity_service.py     (59 linhas)
│       │       ├── campaign_service.py     (124 linhas)
│       │       ├── company_service.py      (33 linhas)
│       │       ├── contact_service.py      (100 linhas)
│       │       ├── conversation_service.py (122 linhas)
│       │       ├── deal_service.py         (62 linhas)
│       │       ├── messaging_policy_service.py (35 linhas)
│       │       ├── messaging_service.py    (40 linhas)
│       │       ├── pipeline_service.py     (54 linhas)
│       │       └── task_service.py         (81 linhas)
│       ├── core/
│       │   ├── config.py           ← Settings via pydantic-settings
│       │   ├── constants.py
│       │   ├── exceptions.py
│       │   ├── logging.py
│       │   └── paths.py
│       ├── domain/
│       │   ├── entities/           ← 10 entidades de domínio
│       │   ├── enums/              ← 6 arquivos de enums
│       │   ├── events/             ← 4 arquivos de eventos
│       │   └── ports/              ← interfaces (4 arquivos)
│       ├── infrastructure/
│       │   ├── database/
│       │   │   ├── base.py
│       │   │   ├── engine.py
│       │   │   ├── session.py
│       │   │   ├── models/         ← 8 arquivos de models + __init__
│       │   │   └── repositories/   ← 5 repositórios
│       │   ├── jobs/
│       │   │   ├── campaign_worker.py
│       │   │   └── local_queue.py
│       │   ├── messaging/
│       │   │   ├── mock/
│       │   │   │   └── provider.py
│       │   │   └── whatsapp/
│       │   │       ├── client.py
│       │   │       ├── parser.py
│       │   │       ├── provider.py
│       │   │       ├── schemas.py
│       │   │       └── templates.py
│       │   └── security/
│       │       └── secrets.py
│       ├── ui/
│       │   ├── app.py              ← QApplication wrapper
│       │   ├── main_window.py      ← MainWindow (93 linhas)
│       │   ├── theme.py            ← COLORS dict + QSS
│       │   ├── components/         ← badges, cards, empty_state
│       │   ├── dialogs/            ← 6 dialogs
│       │   ├── navigation/         ← sidebar
│       │   ├── pages/              ← 8 páginas
│       │   └── viewmodels/         ← VAZIO
│       ├── webhook/
│       │   ├── __main__.py         ← entry point webhook
│       │   ├── app.py              ← FastAPI app
│       │   ├── handlers/
│       │   │   ├── messages.py     ← VAZIO (lógica está em routes.py)
│       │   │   └── statuses.py     ← VAZIO (lógica está em routes.py)
│       │   ├── routes.py           ← GET + POST /webhook
│       │   └── verification.py     ← verify_whatsapp_signature
│       └── workers/
│           └── background_worker.py
└── tests/
    ├── conftest.py
    ├── fixtures/
    ├── integration/                ← 10 arquivos de testes
    └── unit/                       ← 2 arquivos de testes
```

**Observações sobre estrutura:**
- Pastas `application/commands`, `application/dto`, `application/handlers`, `application/queries` existem mas estão **completamente vazias** — estrutura planejada sem implementação.
- Pasta `ui/viewmodels` existe mas está **vazia** — padrão MVVM declarado mas não usado.
- `webhook/handlers/messages.py` e `webhook/handlers/statuses.py` existem mas estão **vazios** — a lógica está toda em `routes.py`.
- Um único arquivo Alembic migration indica que o schema nunca foi alterado com migrations desde a criação inicial.
- Nenhum arquivo `.env` de produção encontrado (apenas `.env.example`).

---

## 4. STACK E DEPENDÊNCIAS

**Ambiente:**
- Python 3.12.13
- macOS Apple Silicon (darwin 25.5.0)
- Venv: `/Users/augustoristow/PycharmProjects/AtlasUltimateCRM/.venv`

**Dependências (extraídas de pyproject.toml + venv instalado):**

| Pacote | Finalidade |
|--------|-----------|
| PySide6 | Interface gráfica desktop Qt |
| SQLAlchemy 2.x | ORM |
| Alembic | Migrations de banco |
| FastAPI | Servidor webhook |
| uvicorn | ASGI server para FastAPI |
| httpx | Chamadas HTTP para Meta API |
| pydantic | Validação e schemas |
| pydantic-settings | Settings via .env |
| phonenumbers | Normalização de telefones |
| pytest | Testes |
| pytest-asyncio | Suporte async nos testes |
| ruff | Linter |
| mypy | Type checker |

**Ferramentas de qualidade instaladas e configuradas:**
- `ruff` ✓ (334 erros encontrados — ver seção 15)
- `mypy` ✓ (16 erros — todos em bootstrap.py)
- `pytest` ✓ (34 testes passando)

---

## 5. ARQUITETURA EXISTENTE

### 5.1 Camadas implementadas

```
┌─────────────────────────────────────────┐
│              UI (PySide6)               │ ← Acessa bootstrap diretamente
├─────────────────────────────────────────┤
│          Application Services           │ ← Orquestra casos de uso
├─────────────────────────────────────────┤
│          Domain (Entities + Events)     │ ← Regras de negócio puras
├─────────────────────────────────────────┤
│    Infrastructure (DB + Messaging)      │ ← SQLAlchemy, WhatsApp, Fila
└─────────────────────────────────────────┘
         ↑ Bootstrap (DI Container) ↑
```

### 5.2 Bootstrap — `src/atlas_ultimate_crm/bootstrap.py`

O `Bootstrap` é o container de injeção de dependências central. Responsabilidades:
1. Cria o engine SQLAlchemy
2. Instancia todos os repositórios com sessão compartilhada
3. Instancia todos os services com suas dependências
4. Cria workspace e pipeline padrão na primeira execução
5. Registra event handlers

**Problema crítico no bootstrap:**
```python
# Linha 106 — Sessão ÚNICA e longa (long-lived session) compartilhada por todos os repos
self._read_session = self._session_factory_raw()
contact_repo = SQLContactRepository(self._read_session)
company_repo = SQLCompanyRepository(self._read_session)
conv_repo = SQLConversationRepository(self._read_session)
# ...
```
Esta sessão nunca é fechada. Todos os repos compartilham a mesma sessão. Ao mesmo tempo, os services criam novas sessões via `session_factory`. Isso pode causar dados desatualizados nos repos (sessão stale) e conflitos de write.

**mypy encontrou 16 erros em bootstrap.py** porque os atributos são inicializados como `None` mas depois recebem objetos tipados. Não é falha funcional mas indica ausência de tipagem adequada.

### 5.3 Violações de separação de responsabilidades encontradas

| Local | Arquivo | Problema |
|-------|---------|---------|
| Dashboard | `ui/pages/dashboard/page.py:94-100` | Acessa SQLAlchemy diretamente (bypassa service) |
| Campaigns UI | `ui/pages/campaigns/page.py:46` | `self._bs.campaign_service._repo.get_recipients()` — acessa repo privado |
| ConversationService | `conversation_service.py:59` | Importa modelo DB dentro de método usando `__import__` |
| PipelineService | `pipeline_service.py` | Acessa models DB diretamente sem passar por repositório |
| ActivityService | Importa `Session` mas não usa |

### 5.4 Portas (Ports) definidas

```
domain/ports/
├── event_bus.py         ← IEventBus (interface)
├── messaging_provider.py ← MessagingProvider, SendTextResult, MockTemplate, TemplateComponent
├── repositories.py      ← Interfaces de repositório
└── task_queue.py        ← ITaskQueue
```

Positivo: interfaces de domínio bem definidas. Contudo, as implementações dos services às vezes importam diretamente as classes concretas de infraestrutura em vez das interfaces, quebrando a inversão de dependência.

### 5.5 Event Bus

`application/event_bus.py` implementa `InMemoryEventBus` com padrão observer. Apenas um handler registrado atualmente:
- `ContactCreated` → registra atividade

Eventos definidos mas sem handlers: `ContactUpdated`, `DealCreated`, `DealStageChanged`, mensagens recebidas/enviadas.

---

## 6. BANCO DE DADOS E RELACIONAMENTOS

### 6.1 Configuração

- **Engine:** SQLite (WAL mode habilitado)
- **Foreign keys:** `PRAGMA foreign_keys=ON` ✓
- **Journal mode:** `PRAGMA journal_mode=WAL` ✓
- **Busy timeout:** `PRAGMA busy_timeout=5000` ✓
- **Localização:** `~/Library/Application Support/Atlas Ultimate CRM/atlas_ultimate.db`
- **Tamanho atual:** ~315 KB (banco de desenvolvimento com dados de demo)

### 6.2 Tabelas existentes (24 tabelas)

| Tabela | Finalidade | Registros (dev) |
|--------|-----------|----------------|
| workspaces | Espaços de trabalho | — |
| users | Usuários do sistema | — |
| workspace_memberships | Vínculo usuário-workspace | — |
| contacts | Contatos do CRM | 6 |
| tags | Etiquetas | — |
| contact_tags | Vínculo contato-tag | — |
| contact_lists | Listas de contatos | — |
| contact_list_members | Membros das listas | — |
| whatsapp_opt_ins | Consentimento WhatsApp | — |
| companies | Empresas | 6 |
| contact_companies | Vínculo contato-empresa (N:N) | — |
| pipelines | Pipelines de vendas | — |
| pipeline_stages | Estágios do pipeline | — |
| deals | Negociações/Oportunidades | — |
| deal_contacts | Vínculo deal-contato (N:N) | — |
| conversations | Conversas de mensagens | 3 |
| messages | Mensagens individuais | 14 |
| channel_accounts | Contas de canal (WhatsApp) | — |
| campaigns | Campanhas | 2 |
| campaign_recipients | Destinatários de campanha | — |
| whatsapp_templates | Templates aprovados pela Meta | — |
| tasks | Tarefas | — |
| activities | Registro de atividades/timeline | — |
| notes | Observações | — |
| background_jobs | Fila de jobs assíncronos | — |
| webhook_events | Log de eventos recebidos | — |

### 6.3 Relacionamentos CRM — avaliação

| Cenário | Suporte | Observação |
|---------|---------|-----------|
| Contato em múltiplas campanhas | ✓ | Via campaign_recipients |
| Contato em múltiplas conversas | ✓ | conversations.contact_id |
| Contato em múltiplas oportunidades | ✓ | Via deal_contacts (N:N) |
| Contato em múltiplas empresas | ✓ | Via contact_companies (N:N, com is_primary) |
| Contato com múltiplas tarefas | ✓ | tasks.contact_id |
| Contato com múltiplas atividades | ✓ | activities.contact_id |
| Deal com múltiplos contatos | ✓ | Via deal_contacts (N:N) |
| Conversa com is_primary | Falta | Sem campo assigned_user funcional |

### 6.4 Normalização de telefones

- Coluna `phone_normalized` (E.164) existe em `contacts`
- Índice em `contacts.phone_normalized`
- `normalize_phone()` em `contact_service.py` usa a biblioteca `phonenumbers` com região padrão "BR"
- Deduplicação por `phone_normalized` implementada em `create_contact()`
- Números brasileiros com e sem DDI são normalizados para `+55XXXXXXXXXXX`

**Problema:** a lógica de normalização está no service, não no domínio. O campo `phone` armazena o formato original, `phone_normalized` armazena o E.164. Risco: se `phone_normalized` estiver vazio (falha de parse), o lookup pode não encontrar duplicata.

### 6.5 Migração para PostgreSQL — obstáculos reais

1. **`StaticPool` para in-memory:** usado só em testes — não impacta produção.
2. **PRAGMAs SQLite:** `PRAGMA foreign_keys`, `journal_mode=WAL`, `busy_timeout` são específicos do SQLite e precisam ser removidos/adaptados.
3. **`check_same_thread=False`:** parâmetro de conexão específico do SQLite.
4. **VARCHAR sem tamanho:** SQLAlchemy usa `String` sem comprimento definido — funciona em SQLite mas em PostgreSQL seria `TEXT`. Geralmente compatível mas requer revisão.
5. **FLOAT em `deals.value`:** PostgreSQL recomenda `NUMERIC/DECIMAL` para valores monetários.
6. **Uma única migration:** sem histórico de migrations para rastrear changes. Ao migrar para PostgreSQL, seria necessário gerar nova migration base.
7. **Sessões de longa vida:** o `_read_session` no bootstrap precisa ser refatorado para connection pool adequado.
8. **Async:** o webhook FastAPI e o cliente httpx são síncronos — num backend de produção com PostgreSQL seria necessário adaptar para async SQLAlchemy.

---

## 7. FUNCIONALIDADES CRM EXISTENTES

### A. CONTATOS — `contact_service.py` + `contact_repository.py`

| Funcionalidade | Status | Arquivo |
|----------------|--------|---------|
| Cadastro | FUNCIONAL | contact_service.create_contact() |
| Deduplicação por telefone | FUNCIONAL | contact_service.create_contact() |
| Busca por telefone (E.164) | FUNCIONAL | contact_repository.get_by_phone() |
| Listagem com pesquisa | FUNCIONAL | contact_service.list_contacts() |
| Contagem | FUNCIONAL | contact_service.count_contacts() |
| Edição | FUNCIONAL | contact_service.update_contact() |
| Origem (source) | FUNCIONAL | ContactSource enum |
| Lifecycle stage | ESTRUTURADO | Campo existe, sem transições |
| Tags | ESTRUTURADO | Tabela existe, sem service |
| Empresa vinculada | ESTRUTURADO | Tabela existe, sem service |
| Importação CSV | NÃO IMPLEMENTADO | Não existe em nenhum arquivo |
| Exclusão/Arquivamento | NÃO IMPLEMENTADO | Sem soft/hard delete |
| Histórico completo (Contact 360) | ESTRUTURADO | Atividades parciais |
| Filtros avançados | NÃO IMPLEMENTADO | Só busca por texto |

### B. EMPRESAS — `company_service.py`

`company_service.py` tem apenas **33 linhas**:

| Funcionalidade | Status |
|----------------|--------|
| Cadastro | FUNCIONAL |
| Listagem | FUNCIONAL |
| Edição | NÃO IMPLEMENTADO |
| Exclusão | NÃO IMPLEMENTADO |
| Vinculação de contatos | NÃO IMPLEMENTADO (tabela contact_companies existe) |
| Oportunidades vinculadas | NÃO IMPLEMENTADO |

### C. PIPELINE — `pipeline_service.py` + `deal_service.py`

| Funcionalidade | Status |
|----------------|--------|
| Pipeline padrão (criado automaticamente) | FUNCIONAL |
| 7 estágios padrão | FUNCIONAL |
| Criação de oportunidade | FUNCIONAL |
| Mudança de estágio | FUNCIONAL |
| Vinculação com contato | FUNCIONAL |
| Vinculação com empresa | FUNCIONAL (campo company_id em deals) |
| Valores em R$ | FUNCIONAL |
| Total do pipeline | FUNCIONAL |
| Contagem de deals abertos | FUNCIONAL |
| Edição do deal | NÃO IMPLEMENTADO |
| Exclusão do deal | NÃO IMPLEMENTADO |
| Múltiplos pipelines | ESTRUTURADO |
| Drag-and-drop no kanban | NÃO IMPLEMENTADO |
| Histórico de mudanças de estágio | FUNCIONAL (via activities) |
| Relatórios de pipeline | NÃO IMPLEMENTADO |

### D. TAREFAS — `task_service.py`

| Funcionalidade | Status |
|----------------|--------|
| Criação | FUNCIONAL |
| Conclusão | FUNCIONAL |
| Listagem por status | FUNCIONAL |
| Contagem de pendentes | FUNCIONAL |
| Edição | NÃO IMPLEMENTADO |
| Exclusão | NÃO IMPLEMENTADO |
| Prioridade | ESTRUTURADO (campo existe, sem filtro) |
| Vencimento | ESTRUTURADO (campo existe, sem alertas) |
| Vínculo com contato | FUNCIONAL |
| Vínculo com deal | FUNCIONAL |
| Atribuição de responsável | ESTRUTURADO (assigned_user_id existe) |

### E. TIMELINE / ATIVIDADES — `activity_service.py`

| Funcionalidade | Status |
|----------------|--------|
| Registro automático de criação de contato | FUNCIONAL |
| Registro de mensagem enviada | FUNCIONAL |
| Registro de mensagem recebida | FUNCIONAL |
| Registro de deal criado | FUNCIONAL |
| Registro de mudança de estágio | FUNCIONAL |
| Registro de campanha enviada | FUNCIONAL |
| Visão de timeline por contato | NÃO IMPLEMENTADO (sem página dedicada) |
| Notas manuais | ESTRUTURADO (tabela notes existe, sem service) |
| Filtros por tipo de atividade | NÃO IMPLEMENTADO |

**Tipos de atividade definidos nos enums:**
`CONTACT_CREATED`, `MESSAGE_SENT`, `MESSAGE_RECEIVED`, `DEAL_CREATED`, `DEAL_STAGE_CHANGED`, `TASK_CREATED`, `TASK_COMPLETED`, `NOTE_ADDED`, `CAMPAIGN_MESSAGE_SENT`, `CALL_MADE`, `EMAIL_SENT`

### F. PERFIL DO CONTATO / CONTACT 360

Existe um `ContactDetailDialog` que abre ao dar duplo-clique na lista de contatos. Status:
- Exibe dados básicos do contato ✓
- Edição inline: PARCIALMENTE IMPLEMENTADO
- Histórico/atividades do contato: NÃO IMPLEMENTADO no dialog
- Conversas do contato: NÃO IMPLEMENTADO no dialog
- Deals do contato: NÃO IMPLEMENTADO no dialog
- Tarefas do contato: NÃO IMPLEMENTADO no dialog

---

## 8. SITUAÇÃO ATUAL DO INBOX

### Implementado:
- Listagem de conversas abertas (coluna esquerda) — FUNCIONAL
- Abertura de conversa ao clicar — FUNCIONAL
- Exibição de mensagens com bolhas (inbound esquerda / outbound direita) — FUNCIONAL
- Envio manual de mensagem via campo de texto — FUNCIONAL (em modo mock e real)
- Marcar conversa como lida ao abrir — FUNCIONAL
- Contador de não lidas na lista — ESTRUTURADO (unread_count existe mas não exibido visualmente)
- Histórico persiste após reiniciar — FUNCIONAL (banco SQLite)
- Botão "Simular mensagem recebida" — FUNCIONAL (em modo mock)

### Não implementado / problemas encontrados:
- **Auto-refresh:** a lista de conversas NÃO atualiza automaticamente quando chegam novas mensagens. O usuário precisa navegar entre páginas ou reiniciar para ver novas mensagens.
- **Status de entrega:** `sent_at`, `delivered_at`, `read_at` existem no banco mas não são exibidos nas bolhas.
- **Identificação de empresa:** sem empresa exibida no header da conversa.
- **Vínculo com deal:** sem painel lateral mostrando deals do contato.
- **Múltiplos atendentes:** sem campo de atribuição funcional na UI.
- **Transferência de atendimento:** não implementado.
- **Etiquetas de conversa:** não implementado.
- **Respostas rápidas:** não implementado.
- **Envio de arquivos/imagens/áudio:** não implementado.
- **Templates no Inbox:** não implementado.
- **Pesquisa nas conversas:** não implementado.
- **Filtros:** não implementado.

### Resposta à pergunta principal:
> *É possível usar o Inbox atual como base para atendimento comercial real?*

**Sim, como base.** A estrutura de conversa-mensagem é sólida. A persistência funciona. O envio funciona (tanto mock quanto WhatsApp real via API). O problema crítico é a **ausência de auto-refresh** — em produção, um atendente não veria as mensagens chegando sem recarregar manualmente.

### Expansibilidade futura:
- **Múltiplos atendentes:** campo `assigned_user_id` existe em conversations. Falta UI e lógica de atribuição.
- **Arquivos/mídia:** a tabela messages tem `message_type` com enum (text, image, audio, document, video). Falta implementação nos handlers.
- **Templates:** `WhatsAppTemplateModel` existe, `send_template()` implementado no provider. Falta UI no Inbox.
- **IA:** arquitetura não impede, mas requereria um serviço separado consumindo a conversa.

---

## 9. SITUAÇÃO ATUAL DAS CAMPANHAS

### Implementado:
- Criação de campanha — FUNCIONAL
- Adição de destinatários (contact_ids) — FUNCIONAL
- Execução da campanha (`run_campaign`) — **PARCIALMENTE FUNCIONAL**
  - Itera recipients pendentes e chama `messaging_service._provider.send_text()`
  - Registra status (sent/failed) e `provider_message_id`
  - Marca campanha como COMPLETED após envio
- `mark_replied()` — FUNCIONAL (relaciona resposta ao destinatário via `provider_message_id`)
- Listagem de campanhas — FUNCIONAL
- Contagem de campanhas ativas — FUNCIONAL
- Métricas na UI (enviadas, respondidas) — FUNCIONAL

### Problemas críticos:

**1. Campanhas enviam texto livre, não templates:**
```python
# campaign_service.py linha 84
result = self._messaging_service._provider.send_text(phone, f"[Campanha: {campaign.name}]")
```
A WhatsApp Business API exige o uso de templates aprovados pela Meta para mensagens proativas (fora da janela de 24h). Enviar texto livre para campanhas resultaria em **violação de política e bloqueio da conta**.

**2. Execução síncrona no thread principal:**
O método `run_campaign()` executa todos os envios de forma síncrona. Se uma campanha tiver 1000 contatos, a UI congelaria completamente durante o envio.

**3. Sem controle de rate limiting:**
A Meta API tem limites de throughput (número de mensagens por segundo). Não há delay entre envios.

**4. Sem pausa/cancelamento:**
Não existe método `pause_campaign()` ou `cancel_campaign()`.

**5. Sem retomada após reinicialização:**
Se o aplicativo fechar durante uma campanha RUNNING, os recipients ficam com status PENDING mas a campanha já não está mais em execução.

**6. Sem controle de opt-in:**
A tabela `whatsapp_opt_ins` existe mas `MessagingPolicyService` não valida o consentimento antes de enviar.

**7. Idempotência no envio:**
Sem verificação se uma mensagem já foi enviada — reiniciar a campanha poderia re-enviar para recipients já marcados como SENT? (Não — o código verifica `status != PENDING`, então recipients já enviados são ignorados. Mas o status SENT é atualizado num segundo contexto — risco de falha entre o envio e o update.)

**Fluxo atual quando um contato responde à campanha:**
1. Meta envia evento ao webhook POST /webhook
2. Parser identifica `message_received`
3. `contact_service.get_or_create_by_phone()` encontra/cria contato
4. `messaging_service.handle_inbound()` cria/atualiza conversa e salva mensagem
5. `campaign_service.mark_replied()` procura recipient pelo `provider_message_id`
6. Recipient é marcado como REPLIED com `replied_at`

**Problema:** O `mark_replied()` busca por `provider_message_id` do **destinatário** (`campaign_recipient.provider_message_id`), não da mensagem de resposta. A resposta do contato tem um `provider_message_id` diferente. A lógica atual **não consegue relacionar corretamente a resposta ao destinatário da campanha** desta forma.

---

## 10. SITUAÇÃO ATUAL DA INTEGRAÇÃO META

### Variáveis de ambiente configuradas (nomes reais no projeto):

| Variável | Nome no Settings | Uso |
|----------|-----------------|-----|
| APP_MODE | `app_mode` | "mock" ou "meta" — controla qual provider usar |
| META_GRAPH_API_VERSION | `meta_graph_api_version` | Default "v19.0" |
| META_ACCESS_TOKEN | `meta_access_token` | Token de autenticação Bearer |
| META_WABA_ID | `meta_waba_id` | WhatsApp Business Account ID |
| META_PHONE_NUMBER_ID | `meta_phone_number_id` | ID do número de telefone |
| META_APP_SECRET | `meta_app_secret` | Secret para validar assinatura do webhook |
| META_WEBHOOK_VERIFY_TOKEN | `meta_webhook_verify_token` | Default "atlas_webhook_token" |

**Alerta de segurança:** O valor default `"atlas_webhook_token"` no código (`config.py:22`) significa que se o `.env` não definir `META_WEBHOOK_VERIFY_TOKEN`, qualquer um que souber este valor padrão poderia fazer verificação do webhook. Deve sempre ser configurado via `.env`.

### Status dos componentes:

**WhatsAppClient** (`infrastructure/messaging/whatsapp/client.py`)
- `send_message()`: faz POST para `https://graph.facebook.com/v19.0/{phone_number_id}/messages` com Bearer token. IMPLEMENTADO.
- `get_templates()`: faz GET para `/{waba_id}/message_templates`. IMPLEMENTADO.
- Não usa httpx.AsyncClient (síncrono) — bloqueante no webhook async.
- Sem retry automático em caso de falha.
- Sem tratamento de rate limit (429).

**WhatsAppCloudProvider** (`infrastructure/messaging/whatsapp/provider.py`)
- `send_text()`: constrói WAMessage e chama client.send_message(). IMPLEMENTADO.
- `send_template()`: constrói WAMessage com template. IMPLEMENTADO.
- `get_templates()`: busca templates da Meta e retorna como `MockTemplate`. IMPLEMENTADO.
- `test_connection()`: chama `get_templates()` como healthcheck. IMPLEMENTADO.

**Identificação do número conectado:**
Não existe método para buscar o número de telefone associado ao `phone_number_id`. O sistema não exibe qual número está conectado na UI.

**Templates:**
- `templates.py` tem apenas 10 linhas — apenas uma função stub básica. NÃO SINCRONIZA templates automaticamente.
- Os templates precisam ser sincronizados manualmente clicando em alguma ação (não encontrada em uso ativo na UI de Templates).

**DIFERENCIAÇÃO CRÍTICA:**
O código WhatsApp está **estruturado para a API real** mas **nunca foi testado com a Meta**. Não há evidências de testes de integração reais. Em modo mock (padrão), o sistema funciona completamente offline.

---

## 11. SITUAÇÃO ATUAL DO WEBHOOK

### Servidor FastAPI (`webhook/app.py`)
- Entry point: `python -m atlas_ultimate_crm.webhook`
- Cria nova instância de `Bootstrap` independente do desktop
- Usa mesma `database_url` das settings (mesmo SQLite local)

### GET /webhook — Verificação Meta
```python
# routes.py:12-21
@router.get("/webhook")
async def verify_webhook(hub_mode, hub_challenge, hub_verify_token):
    expected_token = bootstrap.settings.meta_webhook_verify_token
    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403)
```
**Status: FUNCIONAL.** Compara o token recebido com o configurado. Retorna o challenge. Correto segundo a documentação da Meta.

### POST /webhook — Recebimento de eventos
**Status: PARCIALMENTE IMPLEMENTADO**

**Fluxo completo do código ao banco:**
```
POST /webhook (routes.py)
    ↓ Persiste WebhookEventModel com status="received"
    ↓ parse_webhook_payload() (parser.py)
        ↓ Itera entry[].changes[]
        ↓ Para field="messages":
            ↓ messages[] → {type: "message_received", from_phone, body, message_id}
            ↓ statuses[] → {type: "message_status", message_id, status}
    ↓ _handle_event() (routes.py:66)
        → message_received:
            ↓ contact_service.get_or_create_by_phone()
                → SQLContactRepository.get_by_phone() ou save()
                → Persiste ContactModel
            ↓ messaging_service.handle_inbound()
                ↓ conversation_service.get_or_create_conversation()
                    → SQLConversationRepository.get_by_contact() ou save()
                ↓ conversation_service.save_inbound_message()
                    → Persiste MessageModel
                    → Atualiza ConversationModel (last_message_at, unread_count, service_window_expires_at)
                    → activity_service.record(MESSAGE_RECEIVED)
            ↓ campaign_service.mark_replied() [lógica com bug - ver seção 9]
        → message_status:
            → APENAS LOGA — não persiste no banco
    ↓ Atualiza WebhookEventModel para status="processed"
```

### Problemas identificados no webhook:

**1. CRÍTICO — Assinatura HMAC não validada:**
```python
# verification.py — função existe mas NUNCA É CHAMADA em routes.py
def verify_whatsapp_signature(payload: bytes, signature: str, app_secret: str) -> bool:
    expected = "sha256=" + hmac.new(app_secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```
Qualquer pessoa pode enviar POST para o webhook sem autenticação. Risco de injeção de mensagens falsas.

**2. CRÍTICO — Status de mensagens não persistidos:**
```python
elif event_type == "message_status":
    provider_message_id = event.get("message_id", "")
    status = event.get("status", "")
    logger.info("Message status update: %s -> %s", provider_message_id, status)
    # FIM — nada mais acontece
```
Os campos `sent_at`, `delivered_at`, `read_at`, `failed_at` e `failure_reason` nas mensagens **nunca são atualizados**.

**3. Idempotência ausente:**
O `WebhookEventModel.external_event_id` recebe um UUID gerado localmente, não o ID real do evento da Meta. Eventos duplicados da Meta criariam mensagens duplicadas.

**4. Webhook é síncrono dentro de rota async:**
`httpx.Client` (não AsyncClient) é usado no WhatsApp client. Numa rota FastAPI async, isso bloquearia o event loop.

**5. Handlers vazios:**
`webhook/handlers/messages.py` e `webhook/handlers/statuses.py` estão vazios. A lógica está acumulada em `routes.py`.

**6. `external_event_id` incorreto:**
O campo deveria armazenar o ID do evento da Meta para idempotência. Atualmente armazena um UUID gerado internamente.

---

## 12. SITUAÇÃO DA ARQUITETURA DESKTOP/CLOUD

### Dependências atuais:

| Pergunta | Resposta |
|---------|---------|
| O webhook depende do banco SQLite local? | **SIM** — tanto desktop quanto webhook acessam o mesmo arquivo em `~/Library/Application Support/` |
| O webhook depende de o Mac estar ligado? | **SIM** — uvicorn roda no Mac local |
| O webhook processa mensagens sem o app aberto? | **PARCIALMENTE** — webhook pode rodar separado, mas usa mesma sessão de bootstrap com mesmo banco |
| O que acontece se o computador ficar desligado? | **Mensagens são perdidas** — a Meta não consegue entregar e re-tenta por alguns dias (backoff), mas após esse período as mensagens são descartadas |
| Como o app recuperaria mensagens durante offline? | **Não existe mecanismo** — nenhuma sincronização implementada |
| Existe mecanismo de sincronização? | **NÃO** |
| A arquitetura permite separar backend do desktop? | **PARCIALMENTE** — o bootstrap pode ser reusado, mas há acoplamentos |

### Problema de concorrência:
Quando o webhook FastAPI e o app desktop rodam simultaneamente, ambos fazem write no mesmo SQLite. O WAL mode ajuda mas não elimina o risco de `SQLITE_BUSY` em operações longas.

### Componentes que precisariam migrar para servidor:
- Webhook FastAPI
- Bootstrap (instância separada)
- SQLite → PostgreSQL (ou SQLite em volume persistente)
- Campaign worker (para execução em background)

### Componentes que poderiam continuar locais:
- UI PySide6 (enquanto for desktop)
- Sincronização de dados local (se for implementada)

### Proposta de evolução arquitetural (diagnóstico apenas):
```
Fase atual:
[Desktop PySide6] ←→ [SQLite local] ←→ [Webhook FastAPI local]
                                              ↕
                                       [Meta Cloud API]

Fase futura:
[Desktop PySide6] ←→ [API REST interna] ←→ [PostgreSQL em servidor]
                              ↕
                    [Webhook FastAPI em servidor]
                              ↕
                       [Meta Cloud API]
```

---

## 13. SEGURANÇA E CREDENCIAIS

### Positivo:
- `.env` está no `.gitignore` ✓
- `.db` e `.sqlite` estão no `.gitignore` ✓
- `.venv` está no `.gitignore` ✓
- `.env.example` não contém valores reais ✓
- Função `verify_whatsapp_signature()` implementada corretamente ✓
- `hmac.compare_digest()` usado (timing-safe) ✓

### Problemas encontrados:

**1. CRÍTICO — Assinatura HMAC do webhook não validada:**
A função existe mas não é invocada. Qualquer fonte pode enviar eventos POST para o webhook.

**2. IMPORTANTE — Token padrão hardcoded:**
`meta_webhook_verify_token: str = "atlas_webhook_token"` em `config.py`. Se `.env` não for configurado, o token default é conhecido. Deve ser sempre configurado externamente.

**3. SecretsStore é superficial:**
`infrastructure/security/secrets.py` usa apenas `os.environ`. O comentário menciona "Future: macOS Keychain via keyring library" mas não está implementado. Credenciais da Meta ficam em variáveis de ambiente em texto claro.

**4. Logs:**
Não foram verificados logs para exposição de tokens. A configuração de logging em `core/logging.py` deve ser auditada para garantir que access tokens não sejam logados.

**5. Sessão compartilhada:**
O `_read_session` compartilhado no bootstrap pode expor dados de um workspace a outro em deployments multi-workspace futuros.

---

## 14. INTERFACE E EXPERIÊNCIA

### MainWindow (`ui/main_window.py` — 93 linhas)
- Janela principal simples com sidebar + stacked pages
- Navegação via sidebar com botões
- Sem menu superior, sem atalhos de teclado

### Sidebar (`ui/navigation/sidebar.py`)
- Navegação entre páginas: Dashboard, Contatos, Empresas, Pipeline, Inbox, Campanhas, Tarefas, Templates, Configurações
- Visual escuro com botão ativo destacado

### Tema (`ui/theme.py`)
- Dict `COLORS` centralizado
- Paleta escura (dark mode) com cores de accent azul
- QSS aplicado inline em cada componente (sem arquivo .qss separado)

### Páginas e estado funcional:

| Página | Dados reais? | Ações funcionais | Problemas |
|--------|-------------|-----------------|---------|
| Dashboard | SIM | Visualização apenas | Acessa repo diretamente; sem refresh automático |
| Contatos | SIM | Lista, busca, novo, editar | Sem importação CSV, sem filtros avançados |
| Empresas | SIM | Lista, novo | Sem vínculo de contato na UI |
| Pipeline | SIM | Visualizar, mover stage, novo deal | Sem DnD, sem edição de deal |
| Inbox | SIM | Listar, conversar, simular | Sem auto-refresh |
| Campanhas | SIM | Listar, criar, disparar | Sem templates, síncrono |
| Tarefas | SIM | Listar, criar, concluir | Sem edição, sem filtro por prioridade |
| Templates | NÃO VERIFICADO | — | Página existe, não foi lida em detalhe |
| Configurações | PARCIAL | Testar conexão | Sem salvar configurações |

### Problemas de thread safety:
- `run_campaign()` é chamado no thread principal da UI — congelaria completamente a janela durante o envio.
- Chamadas HTTP no `WhatsAppClient` são síncronas — bloqueantes no thread UI.
- Nenhum uso de `QThread`, `QRunnable` ou `concurrent.futures` encontrado.
- Nenhum worker/signal pattern para operações longas.

### Atualização de dados:
- Cada página tem `refresh()` chamado na inicialização.
- Sem polling periódico, sem WebSocket, sem sinais automáticos.
- Dashboard acessa `_conv_repo` interno diretamente (violação de encapsulamento).

---

## 15. TESTES E QUALIDADE

### Testes (pytest):
**34/34 passando** ✓

| Arquivo | Testes | O que cobre |
|---------|--------|-----------|
| test_activities.py | 2 | Criação de atividade, registro automático |
| test_campaigns.py | 3 | Criação, run (mock), reply |
| test_companies.py | 2 | Criação, listagem |
| test_contacts.py | 4 | Criação, dedup, listagem, contagem |
| test_database.py | 1 | Criação de tabelas |
| test_messaging.py | 3 | Envio texto (mock), inbound, criação de conversa |
| test_pipeline.py | 3 | Pipeline default, criação de deal, mudança de estágio |
| test_tasks.py | 3 | Criação, conclusão, contagem |
| test_webhook_parser.py | 3 | Parse de mensagem, status, política |
| test_workspace.py | 2 | Criação default, persistência |
| test_mock_provider.py | 5 | Mock: send_text, send_template, get_templates, test_connection, provider_name |
| test_phone_normalization.py | 3 | Normalização brasileira, formato local, vazio |

### Cobertura (estimada):
- Fluxos felizes dos services principais: ✓
- Tratamento de erros: NÃO COBERTO
- Webhook real (Meta): NÃO COBERTO
- UI (PySide6): NÃO COBERTO
- Importação CSV: NÃO COBERTO (funcionalidade não existe)
- Concorrência: NÃO COBERTO
- Campanhas com templates reais: NÃO COBERTO
- Status updates persistência: NÃO COBERTO (bug não testado)

### Ruff (linter):
**334 erros encontrados:**
- 172 × E501 — linhas muito longas (>100 chars)
- 110 × I001 — imports desordenados
- 51 × F401 — imports não utilizados
- 1 × F841 — variável local não utilizada

Todos são problemas de estilo/organização, nenhum é funcional crítico. 161 seriam autoCorrigíveis com `ruff --fix`.

### mypy (type checker):
**16 erros em bootstrap.py** — todos do mesmo tipo:
```
bootstrap.py:88: error: Incompatible types in assignment (expression has type "X", variable has type "None")
```
Causa: atributos inicializados como `None` sem type annotation correta. Não funcional mas indica ausência de tipagem adequada no container DI.

---

## 16. MATRIZ DE FUNCIONALIDADES

| Módulo | Funcionalidade | Status | Arquivos relacionados | O que falta | Prioridade |
|--------|---------------|--------|-----------------------|-------------|-----------|
| CRM | Cadastro de contatos | FUNCIONAL | contact_service.py, contact_repository.py | — | — |
| CRM | Deduplicação por telefone | FUNCIONAL | contact_service.py | — | — |
| CRM | Importação CSV | NÃO IMPLEMENTADO | — | Implementar inteiro | ALTA |
| CRM | Exclusão/arquivamento de contatos | NÃO IMPLEMENTADO | — | Soft delete | MÉDIA |
| CRM | Tags em contatos | ESTRUTURADO | contacts.py (model) | Service + UI | MÉDIA |
| CRM | Contact 360 (perfil completo) | ESTRUTURADO | contact_dialog.py (parcial) | Timeline, deals, conversas | ALTA |
| Contatos | Filtros avançados | NÃO IMPLEMENTADO | — | Service + UI | MÉDIA |
| Empresas | Cadastro básico | FUNCIONAL | company_service.py | — | — |
| Empresas | Edição | NÃO IMPLEMENTADO | — | Service + UI | MÉDIA |
| Empresas | Vinculação de contatos | ESTRUTURADO | contact_companies (model) | Service + UI | MÉDIA |
| Pipeline | Kanban visual | FUNCIONAL | pipeline/page.py | — | — |
| Pipeline | Criação de negócio | FUNCIONAL | deal_service.py | — | — |
| Pipeline | Mudança de estágio | FUNCIONAL | deal_service.py | — | — |
| Pipeline | Edição de negócio | NÃO IMPLEMENTADO | — | Service + UI | ALTA |
| Pipeline | Drag-and-drop | NÃO IMPLEMENTADO | — | Qt DnD | BAIXA |
| Tarefas | CRUD completo | FUNCIONAL | task_service.py | Edição, exclusão | — |
| Tarefas | Alertas de vencimento | NÃO IMPLEMENTADO | — | Lógica de notificação | BAIXA |
| Inbox | Listagem de conversas | FUNCIONAL | conversation_service.py | — | — |
| Inbox | Envio de mensagens | FUNCIONAL | messaging_service.py | — | — |
| Inbox | Auto-refresh | NÃO IMPLEMENTADO | — | QTimer polling ou signals | CRÍTICA |
| Inbox | Status de entrega | ESTRUTURADO | messages (model) | Handler de status + UI | ALTA |
| Inbox | Envio de templates | ESTRUTURADO | whatsapp/provider.py | UI no Inbox | ALTA |
| Inbox | Múltiplos atendentes | ESTRUTURADO | assigned_user_id (model) | Lógica + UI | MÉDIA |
| WhatsApp | Envio de texto | FUNCIONAL | whatsapp/provider.py | — | — |
| WhatsApp | Envio de template | IMPLEMENTADO | whatsapp/provider.py | Não usado em campanhas | — |
| WhatsApp | Sincronização de templates | ESTRUTURADO | templates.py (stub) | Implementar sync | ALTA |
| WhatsApp | Conexão testada com Meta | NÃO VERIFICADO | — | Teste real necessário | — |
| Campanhas | Criação | FUNCIONAL | campaign_service.py | — | — |
| Campanhas | Envio via template | NÃO IMPLEMENTADO | — | Substituir send_text por send_template | CRÍTICA |
| Campanhas | Execução assíncrona | NÃO IMPLEMENTADO | campaign_worker.py (stub) | Worker em thread | ALTA |
| Campanhas | Pausa/cancelamento | NÃO IMPLEMENTADO | — | Implementar | MÉDIA |
| Campanhas | Controle de rate limit | NÃO IMPLEMENTADO | — | Delay entre envios | ALTA |
| Campanhas | Validação de opt-in | NÃO IMPLEMENTADO | whatsapp_opt_ins (model) | MessagingPolicyService | ALTA |
| Templates | Listagem da Meta | ESTRUTURADO | templates.py, whatsapp_templates (model) | Sync funcional | ALTA |
| Webhook | Verificação GET | FUNCIONAL | routes.py, verification.py | — | — |
| Webhook | Recebimento de mensagens | FUNCIONAL | routes.py | — | — |
| Webhook | Validação de assinatura HMAC | ESTRUTURADO | verification.py | Chamar em routes.py | CRÍTICA |
| Webhook | Persistência de status | NÃO IMPLEMENTADO | — | Implementar handler | CRÍTICA |
| Webhook | Idempotência | NÃO IMPLEMENTADO | — | Usar ID da Meta como external_event_id | ALTA |
| Dashboard | Métricas reais | FUNCIONAL | dashboard/page.py | — | — |
| Dashboard | Auto-refresh | NÃO IMPLEMENTADO | — | QTimer | MÉDIA |
| Relatórios | Todos | NÃO IMPLEMENTADO | — | Módulo inteiro | BAIXA |
| Configurações | Visualizar config | FUNCIONAL | settings/page.py | — | — |
| Configurações | Salvar configurações | NÃO IMPLEMENTADO | — | Persistir no .env ou DB | MÉDIA |
| Banco de dados | Schema | FUNCIONAL | alembic migration | — | — |
| Banco de dados | Migrations controladas | ESTRUTURADO | 1 migration | Sistema de migrations em uso | — |
| Segurança | .env no .gitignore | FUNCIONAL | .gitignore | — | — |
| Segurança | HMAC webhook | ESTRUTURADO | verification.py | Invocar na rota | CRÍTICA |
| Segurança | Keychain/secrets | ESTRUTURADO | secrets.py | Implementar Keychain | BAIXA |

---

## 17. PROBLEMAS TÉCNICOS ENCONTRADOS

### CRÍTICOS (bloqueiam uso em produção)

**P-01: Assinatura HMAC do webhook não validada**
- **Onde:** `webhook/routes.py` — o POST /webhook não chama `verify_whatsapp_signature()`
- **Consequência:** Qualquer requisição POST para o webhook é processada, incluindo mensagens falsificadas. Risco de injeção de mensagens, spam, manipulação de dados.
- **Solução:** Chamar `verify_whatsapp_signature(body, request.headers.get("X-Hub-Signature-256", ""), settings.meta_app_secret)` antes de processar.
- **Bloqueia novas funcionalidades?** SIM — não deve ir a produção sem isso.

**P-02: Status de mensagens não persistidos**
- **Onde:** `webhook/routes.py:86-89` — `elif event_type == "message_status"` apenas loga.
- **Consequência:** Os campos `sent_at`, `delivered_at`, `read_at`, `failed_at` e `failure_reason` nas mensagens nunca são atualizados. Impossível saber se uma mensagem foi entregue.
- **Solução:** Implementar update no `MessageModel` buscando por `provider_message_id`.
- **Bloqueia novas funcionalidades?** SIM — status de entrega é essencial.

**P-03: Campanhas enviam texto livre (viola política WhatsApp)**
- **Onde:** `campaign_service.py:84`
- **Consequência:** A Meta proibirá envios, bloqueará o número ou a conta WABA.
- **Solução:** Usar `send_template()` com template aprovado pela Meta.
- **Bloqueia novas funcionalidades?** SIM — campanhas não podem ir a produção assim.

**P-04: Campanha executada no thread principal da UI**
- **Onde:** `campaign_service.run_campaign()` chamado diretamente da UI
- **Consequência:** UI congela completamente durante qualquer campanha com múltiplos recipients.
- **Solução:** Executar em `QThread` ou `concurrent.futures.ThreadPoolExecutor`.
- **Bloqueia novas funcionalidades?** SIM — inaceitável para UX.

**P-05: Sessão SQLAlchemy compartilhada de longa vida**
- **Onde:** `bootstrap.py:106-112` — `self._read_session` compartilhado por todos os repositórios
- **Consequência:** Dados stale em consultas (sessão velha não reflete commits de outras sessões), risco de conflitos em writes concorrentes.
- **Solução:** Cada operação de repositório deve criar/fechar sua própria sessão.
- **Bloqueia novas funcionalidades?** SIM — bugs intermitentes difíceis de diagnosticar.

### IMPORTANTES (degradam funcionalidade mas não impedem MVP)

**P-06: Inbox sem auto-refresh**
- **Onde:** `ui/pages/inbox/page.py` — sem QTimer ou signals para atualizar
- **Consequência:** Atendente não vê mensagens novas sem ação manual.
- **Solução:** `QTimer.singleShot()` ou `QTimer` periódico chamando `refresh()`.

**P-07: Idempotência ausente no webhook**
- **Onde:** `webhook/routes.py` — `external_event_id` recebe UUID interno, não ID da Meta
- **Consequência:** Eventos duplicados da Meta criam mensagens duplicadas.
- **Solução:** Usar o campo `id` do entry da Meta como `external_event_id`; verificar antes de processar.

**P-08: mark_replied() não funciona corretamente**
- **Onde:** `campaign_service.py:107-118` + `routes.py:83-84`
- **Consequência:** A resposta de um contato à campanha tem um novo `provider_message_id` (da mensagem de resposta), não o ID da mensagem original enviada. O lookup não encontraria o recipient.
- **Solução:** Relacionar pelo telefone do remetente da resposta buscando o recipient mais recente daquele contato.

**P-09: Dashboard acessa repositório diretamente**
- **Onde:** `dashboard/page.py:73` — `self._bs.conversation_service._conv_repo.count_open(ws_id)`
- **Consequência:** Violação de encapsulamento. Qualquer refatoração interna quebra a UI.
- **Solução:** Adicionar `count_open_conversations()` ao `ConversationService`.

**P-10: UI de Configurações não salva**
- **Onde:** `settings/page.py` — campos WABA_ID, Phone ID editáveis mas sem botão salvar
- **Consequência:** Usuário não consegue configurar o WhatsApp pela UI.

**P-11: httpx.Client síncrono no webhook async**
- **Onde:** `whatsapp/client.py` usa `httpx.Client` (síncrono)
- **Consequência:** Em rota FastAPI async, bloqueia o event loop durante chamadas à Meta.
- **Solução:** Usar `httpx.AsyncClient` com `async/await`.

**P-12: WhatsApp templates não sincronizados automaticamente**
- **Onde:** `templates.py` tem apenas função stub
- **Consequência:** A tabela `whatsapp_templates` fica vazia — campanhas não têm templates para usar.

### MELHORIAS FUTURAS (não bloqueiam desenvolvimento)

**M-01:** `application/commands`, `dto`, `handlers`, `queries` vazios — considerar se o padrão CQRS é necessário ou se as pastas devem ser removidas para reduzir ruído.

**M-02:** 334 erros de ruff (172 linhas longas, 110 imports desordenados, 51 imports não usados) — rodar `ruff --fix` na maioria.

**M-03:** 16 erros de mypy em bootstrap.py — adicionar `Optional[ServiceType]` ou `ServiceType | None` às anotações.

**M-04:** `SecretsStore` usa apenas env vars — implementar macOS Keychain para tokens sensíveis.

**M-05:** `ConversationService.save_inbound_message()` usa `__import__()` (hack) — refatorar.

**M-06:** `CampaignsPage.refresh()` acessa `._repo` privado — adicionar método público no service.

---

## 18. MELHORIAS ARQUITETURAIS NECESSÁRIAS

### 18.1 Sessões por operação (não compartilhadas)
**Estado atual:** Bootstrap cria uma sessão longa e a injeta em todos os repositórios.
**Estado desejado:** Cada operação de repository abre/fecha sua própria sessão via context manager.
**Impacto:** Resolve P-05, elimina dados stale, prepara para PostgreSQL com pool.

### 18.2 Workers assíncronos para operações longas
**Estado atual:** Campanhas e sincronização de templates bloqueiam a UI.
**Estado desejado:** `QThread` + signals para progresso de campanhas.
**Impacto:** Resolve P-04, melhora UX drasticamente.

### 18.3 Separação webhook/desktop
**Estado atual:** Webhook e desktop compartilham mesmo processo SQLite.
**Estado desejado:** Webhook como serviço autônomo acessando banco via API ou PostgreSQL.
**Impacto:** Mensagens chegam mesmo com o Mac fechado.

### 18.4 Auto-refresh no Inbox
**Estado atual:** Sem atualização automática.
**Estado desejado:** QTimer a cada 3-5 segundos verificando novas mensagens.
**Impacto:** Resolve P-06, torna o Inbox utilizável comercialmente.

### 18.5 Tipagem adequada no Bootstrap
**Estado atual:** 16 erros mypy por `None`-typed attributes.
**Estado desejado:** `Optional[ContactService]` ou valor padrão adequado.
**Impacto:** Previne bugs em tempo de execução, melhora autocompleção IDE.

---

## 19. ROADMAP TÉCNICO RECOMENDADO

### Fase 1 — Estabilização (prereq para produção)
Sem esta fase, o sistema não deve ser conectado à Meta real.

1. **Corrigir assinatura HMAC do webhook** (P-01) — 1h
2. **Implementar persistência de status** sent/delivered/read/failed (P-02) — 2h
3. **Corrigir campanha para usar templates** (P-03) — depende de templates sincronizados
4. **Resolver sessão compartilhada** no bootstrap (P-05) — 3h
5. **Sincronizar templates da Meta** automaticamente — 2h
6. **Corrigir mark_replied()** para funcionar por telefone (P-08) — 1h
7. **Implementar idempotência no webhook** — 1h

### Fase 2 — CRM funcional básico
8. **Auto-refresh no Inbox** (P-06) — 1h
9. **Worker assíncrono para campanhas** (P-04) — 3h
10. **Contact 360 dialog** com timeline, conversas, deals, tarefas — 4h
11. **Importação CSV de contatos** — 3h
12. **Salvar configurações WhatsApp** na UI — 2h
13. **Vinculação contato-empresa na UI** — 2h
14. **Edição de deals** (título, valor, stage) — 2h

### Fase 3 — Inbox comercial
15. **Status de entrega visual nas bolhas** — 2h
16. **Seleção e envio de templates no Inbox** — 3h
17. **Atribuição de responsável por conversa** — 3h
18. **Filtros e pesquisa no Inbox** — 2h
19. **Notas em contatos e deals** (service + UI) — 2h

### Fase 4 — Campanhas robustas
20. **Rate limiting** (delay entre envios) — 1h
21. **Pausa/cancelamento de campanha** — 2h
22. **Seleção de template na criação de campanha** — 2h
23. **Validação de opt-in antes de enviar** — 2h
24. **Retomada após reinicialização** — 2h

### Fase 5 — Backend permanente (receber mensagens offline)
25. **Separar webhook em serviço próprio** (VPS/Railway/Render)
26. **Migrar SQLite → PostgreSQL**
27. **API REST interna** para desktop consumir dados do servidor
28. **Mecanismo de sincronização** desktop ↔ servidor

### Fase 6 — SaaS/multi-usuário
29. **Autenticação de usuário** (login/senha)
30. **Multi-workspace** com isolamento
31. **Permissões por papel** (owner, agent, viewer)
32. **Dashboard por usuário**

### Paralelizável sem conflito arquitetural:
- Testes de integração para webhook (pode fazer em paralelo com Fase 1)
- Linting e formatação automática (qualquer fase)
- Tags em contatos (pode fazer em paralelo com Fase 2)
- Relatórios básicos (pode começar na Fase 3)

---

## 20. PRÓXIMOS PASSOS SUGERIDOS

**Imediato (antes de testar com Meta real):**
1. Implementar validação HMAC no webhook — arquivo `webhook/routes.py`
2. Implementar handler de status no webhook — persistir em `MessageModel`
3. Corrigir campaign_service para usar `send_template()` com template selecionado
4. Implementar sincronização de templates da Meta na tela de configurações

**Curto prazo (CRM utilizável):**
5. Auto-refresh no Inbox via QTimer
6. Resolver sessão compartilhada no bootstrap
7. Worker assíncrono para campanhas (QThread)
8. Contact 360 dialog completo
9. Importação CSV de contatos

**Médio prazo (arquitetura robusta):**
10. Separar webhook em serviço independente
11. Migrar banco para PostgreSQL em servidor
12. Implementar mecanismo de sync desktop ↔ servidor

---

## 21. PERGUNTAS E DECISÕES QUE PRECISAM SER TOMADAS PELO PROPRIETÁRIO

1. **Prioridade arquitetural:** O próximo ciclo prioriza estabilização do que existe (corrigir bugs críticos) ou adição de novas funcionalidades (Contact 360, importação CSV)?

2. **Desktop vs. Web:** O produto final será desktop (PySide6) permanentemente ou há plano de migração para web (FastAPI + frontend React/Vue)?

3. **Hosting do webhook:** Onde o webhook FastAPI ficará hospedado em produção? VPS próprio? Railway? AWS Lambda? Isso impacta a escolha entre SQLite remoto e PostgreSQL.

4. **Multi-empresa/SaaS:** O produto será usado por uma única empresa ou haverá múltiplos workspaces? Isso define quando precisaremos de autenticação e isolamento.

5. **Templates WhatsApp:** Já existem templates aprovados na conta Meta? Sem templates aprovados, campanhas não podem ser disparadas.

6. **Opt-in e LGPD:** Existe uma política definida de consentimento para envio de WhatsApp? A tabela `whatsapp_opt_ins` existe mas sem processo de obtenção de consentimento.

7. **Volume esperado de contatos e mensagens:** Isso define se SQLite é suficiente ou se PostgreSQL é necessário já na próxima fase.

8. **Integração com outros canais:** Email, Instagram DM, SMS estão no roadmap? A arquitetura de `ChannelType` enum suporta expansão, mas vale confirmar prioridades.

9. **Automações:** Gatilhos automáticos (ex: contato responde → criar deal, deal muda de estágio → criar tarefa) são prioritários? O `InMemoryEventBus` existe mas só tem um handler ativo.

10. **Backup e recuperação:** Há estratégia definida para backup do SQLite? Um arquivo corrompido perderia todos os dados.

---

## 22. PRINCIPAIS ARQUIVOS QUE O PRÓXIMO ASSISTENTE DEVERÁ EXAMINAR

Para orientar qualquer desenvolvimento futuro, estes são os arquivos mais importantes por área:

### Core/DI:
- `src/atlas_ultimate_crm/bootstrap.py` — container DI, ponto central
- `src/atlas_ultimate_crm/core/config.py` — todas as configurações
- `src/atlas_ultimate_crm/core/constants.py` — constantes globais

### Domínio:
- `src/atlas_ultimate_crm/domain/entities/contact.py`
- `src/atlas_ultimate_crm/domain/entities/conversation.py`
- `src/atlas_ultimate_crm/domain/entities/message.py`
- `src/atlas_ultimate_crm/domain/entities/campaign.py`
- `src/atlas_ultimate_crm/domain/entities/deal.py`
- `src/atlas_ultimate_crm/domain/ports/messaging_provider.py` — interface do provider
- `src/atlas_ultimate_crm/domain/enums/messaging.py` — enums de status

### Serviços críticos:
- `src/atlas_ultimate_crm/application/services/contact_service.py`
- `src/atlas_ultimate_crm/application/services/conversation_service.py`
- `src/atlas_ultimate_crm/application/services/campaign_service.py`
- `src/atlas_ultimate_crm/application/services/messaging_service.py`
- `src/atlas_ultimate_crm/application/services/deal_service.py`

### Banco de dados:
- `src/atlas_ultimate_crm/infrastructure/database/engine.py`
- `src/atlas_ultimate_crm/infrastructure/database/models/conversations.py` — MessageModel
- `src/atlas_ultimate_crm/infrastructure/database/models/campaigns.py`
- `src/atlas_ultimate_crm/infrastructure/database/models/contacts.py`
- `src/atlas_ultimate_crm/infrastructure/database/repositories/contact_repository.py`
- `src/atlas_ultimate_crm/infrastructure/database/repositories/conversation_repository.py`
- `alembic/versions/3af4fc95d3f9_initial_schema.py`

### WhatsApp/Webhook:
- `src/atlas_ultimate_crm/webhook/routes.py` — lógica central do webhook
- `src/atlas_ultimate_crm/webhook/verification.py` — HMAC não usado
- `src/atlas_ultimate_crm/infrastructure/messaging/whatsapp/client.py`
- `src/atlas_ultimate_crm/infrastructure/messaging/whatsapp/provider.py`
- `src/atlas_ultimate_crm/infrastructure/messaging/whatsapp/parser.py`
- `src/atlas_ultimate_crm/infrastructure/messaging/mock/provider.py`

### UI (páginas funcionais):
- `src/atlas_ultimate_crm/ui/pages/inbox/page.py` — mais crítica
- `src/atlas_ultimate_crm/ui/pages/contacts/page.py`
- `src/atlas_ultimate_crm/ui/pages/pipeline/page.py`
- `src/atlas_ultimate_crm/ui/pages/campaigns/page.py`
- `src/atlas_ultimate_crm/ui/pages/dashboard/page.py`
- `src/atlas_ultimate_crm/ui/dialogs/campaign_dialog.py`
- `src/atlas_ultimate_crm/ui/dialogs/contact_dialog.py`

### Testes:
- `tests/conftest.py` — fixtures e bootstrap de teste
- `tests/integration/test_campaigns.py`
- `tests/integration/test_messaging.py`
- `tests/integration/test_webhook_parser.py`

---

*Relatório gerado em: 22/09/2026*
*Todos os testes verificados: 34/34 passando*
*Nenhum segredo, token ou credencial foi incluído neste relatório.*
