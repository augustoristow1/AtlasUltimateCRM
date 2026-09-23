# Import all models so Alembic can detect them
from atlas_ultimate_crm.infrastructure.database.models.workspace import WorkspaceModel, UserModel, WorkspaceMembershipModel  # noqa
from atlas_ultimate_crm.infrastructure.database.models.contacts import ContactModel, TagModel, ContactTagModel, ContactListModel, ContactListMemberModel, WhatsAppOptInModel  # noqa
from atlas_ultimate_crm.infrastructure.database.models.companies import CompanyModel, ContactCompanyModel  # noqa
from atlas_ultimate_crm.infrastructure.database.models.pipelines import PipelineModel, PipelineStageModel, DealModel, DealContactModel  # noqa
from atlas_ultimate_crm.infrastructure.database.models.conversations import ConversationModel, MessageModel, ChannelAccountModel  # noqa
from atlas_ultimate_crm.infrastructure.database.models.campaigns import CampaignModel, CampaignRecipientModel, WhatsAppTemplateModel  # noqa
from atlas_ultimate_crm.infrastructure.database.models.activities import ActivityModel, TaskModel, NoteModel  # noqa
from atlas_ultimate_crm.infrastructure.database.models.system import BackgroundJobModel, WebhookEventModel  # noqa
