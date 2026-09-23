# Atlas Ultimate CRM — Architecture

## Overview

CRM-first desktop application built on Python 3.12, PySide6, SQLAlchemy, and SQLite.
Contact is the central entity. All interactions (messages, deals, tasks) reference Contact.

## Layers

```
UI (PySide6)
  ↓
Application Services
  ↓
Domain (Entities, Enums, Events, Ports)
  ↓
Infrastructure (SQLAlchemy, Messaging Providers, Jobs)
```

## Key Design Decisions

- Contact is never duplicated. CampaignRecipient, Conversation, Deal all point to Contact.id
- InMemoryEventBus for loose coupling between services
- MockMessagingProvider for fully offline operation
- SQLite with WAL mode for desktop performance
- Bootstrap.py as the single DI root

## Future Migration to Cloud

- Replace SQLite engine with PostgreSQL URL
- Replace InMemoryEventBus with Redis Streams or similar
- Replace LocalTaskQueue with Celery or cloud task queues
- Add workspace-level auth (JWT or similar)
