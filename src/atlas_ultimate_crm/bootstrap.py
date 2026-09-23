"""
Central dependency injection and initialization.
Builds all infrastructure, services, and wires them together.
"""
import logging
import uuid
from contextlib import contextmanager
from typing import Any

import atlas_ultimate_crm.infrastructure.database.models  # noqa - registers all models
from atlas_ultimate_crm.core.config import AppMode, get_settings
from atlas_ultimate_crm.core.constants import DEFAULT_USER_NAME, DEFAULT_WORKSPACE_NAME
from atlas_ultimate_crm.core.logging import configure_logging
from atlas_ultimate_crm.infrastructure.database.base import Base
from atlas_ultimate_crm.infrastructure.database.engine import build_engine
from atlas_ultimate_crm.infrastructure.database.session import SessionFactory

logger = logging.getLogger(__name__)


class Bootstrap:
    def __init__(self, database_url: str = "") -> None:
        self.settings = get_settings()
        configure_logging(self.settings.log_level)

        self.engine = build_engine(database_url or self.settings.database_url)
        self._session_factory_raw = SessionFactory(self.engine)

        # Services (populated in _build_services())
        self.event_bus: Any = None
        self.task_queue: Any = None
        self.messaging_provider: Any = None
        self.contact_service: Any = None
        self.company_service: Any = None
        self.activity_service: Any = None
        self.task_service: Any = None
        self.deal_service: Any = None
        self.pipeline_service: Any = None
        self.conversation_service: Any = None
        self.messaging_service: Any = None
        self.messaging_policy_service: Any = None
        self.campaign_service: Any = None
        self.workspace_id: str = ""

    @contextmanager
    def session_context(self):
        session = self._session_factory_raw()
        try:
            yield session
        finally:
            session.close()

    def session_factory(self):
        return self.session_context()

    def initialize(self) -> None:
        logger.info("Initializing Atlas Ultimate CRM...")
        self._create_tables()
        self._build_services()
        self._ensure_default_workspace()
        self._ensure_default_pipeline()
        logger.info("Initialization complete. workspace_id=%s", self.workspace_id)

    def _create_tables(self) -> None:
        Base.metadata.create_all(self.engine)
        logger.info("Database tables ready")

    def _build_services(self) -> None:
        from atlas_ultimate_crm.application.event_bus import InMemoryEventBus
        from atlas_ultimate_crm.application.services.activity_service import ActivityService
        from atlas_ultimate_crm.application.services.campaign_service import CampaignService
        from atlas_ultimate_crm.application.services.company_service import CompanyService
        from atlas_ultimate_crm.application.services.contact_service import ContactService
        from atlas_ultimate_crm.application.services.conversation_service import ConversationService
        from atlas_ultimate_crm.application.services.deal_service import DealService
        from atlas_ultimate_crm.application.services.messaging_policy_service import (
            MessagingPolicyService,
        )
        from atlas_ultimate_crm.application.services.messaging_service import MessagingService
        from atlas_ultimate_crm.application.services.pipeline_service import PipelineService
        from atlas_ultimate_crm.application.services.task_service import TaskService
        from atlas_ultimate_crm.infrastructure.jobs.local_queue import LocalTaskQueue

        self.event_bus = InMemoryEventBus()
        self.task_queue = LocalTaskQueue()

        # Messaging provider
        if self.settings.app_mode == AppMode.MOCK:
            from atlas_ultimate_crm.infrastructure.messaging.mock.provider import (
                MockMessagingProvider,
            )
            self.messaging_provider = MockMessagingProvider()
        else:
            from atlas_ultimate_crm.infrastructure.messaging.whatsapp.client import WhatsAppClient
            from atlas_ultimate_crm.infrastructure.messaging.whatsapp.provider import (
                WhatsAppCloudProvider,
            )
            client = WhatsAppClient(
                access_token=self.settings.meta_access_token,
                phone_number_id=self.settings.meta_phone_number_id,
                api_version=self.settings.meta_graph_api_version,
            )
            self.messaging_provider = WhatsAppCloudProvider(client, self.settings.meta_waba_id)

        self.activity_service = ActivityService(self.session_factory)
        self.contact_service = ContactService(self.event_bus, self.session_factory)
        self.company_service = CompanyService(self.event_bus, self.session_factory)
        self.task_service = TaskService(self.session_factory, self.event_bus)
        self.pipeline_service = PipelineService(self.session_factory)
        self.deal_service = DealService(self.event_bus, self.session_factory, self.activity_service)
        self.conv_service = ConversationService(self.event_bus, self.session_factory, self.activity_service)
        self.conversation_service = self.conv_service
        self.messaging_policy_service = MessagingPolicyService(self.session_factory)
        self.messaging_service = MessagingService(self.messaging_provider, self.conv_service)
        self.campaign_service = CampaignService(self.event_bus, self.session_factory, self.activity_service, self.messaging_service)

        self._register_event_handlers()

    def _register_event_handlers(self) -> None:
        from atlas_ultimate_crm.domain.enums.activities import ActivityType
        from atlas_ultimate_crm.domain.events.contacts import ContactCreated

        def on_contact_created(event):
            self.activity_service.record(
                event.workspace_id, ActivityType.CONTACT_CREATED,
                contact_id=event.contact_id,
                metadata={"name": event.name, "phone": event.phone},
            )

        self.event_bus.subscribe(ContactCreated, on_contact_created)

    def _ensure_default_workspace(self) -> None:
        from sqlalchemy import select

        from atlas_ultimate_crm.infrastructure.database.models.workspace import (
            UserModel,
            WorkspaceMembershipModel,
            WorkspaceModel,
        )

        with self.session_context() as session:
            ws = session.scalars(select(WorkspaceModel)).first()
            if ws:
                self.workspace_id = ws.id
                return

            ws_id = str(uuid.uuid4())
            user_id = str(uuid.uuid4())
            membership_id = str(uuid.uuid4())

            ws = WorkspaceModel(id=ws_id, name=DEFAULT_WORKSPACE_NAME, slug="atlas-studio")
            user = UserModel(id=user_id, workspace_id=ws_id, name=DEFAULT_USER_NAME, role="owner")
            membership = WorkspaceMembershipModel(id=membership_id, workspace_id=ws_id, user_id=user_id, role="owner")

            session.add(ws)
            session.flush()  # ensure workspace is inserted before FK references
            session.add(user)
            session.flush()
            session.add(membership)
            session.commit()
            self.workspace_id = ws_id
            logger.info("Created default workspace: %s", DEFAULT_WORKSPACE_NAME)

    def _ensure_default_pipeline(self) -> None:
        self.pipeline_service.get_or_create_default_pipeline(self.workspace_id)
