from enum import Enum


class ActivityType(str, Enum):
    CONTACT_CREATED = "contact_created"
    CONTACT_UPDATED = "contact_updated"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    CAMPAIGN_ENTERED = "campaign_entered"
    CAMPAIGN_MESSAGE_SENT = "campaign_message_sent"
    CAMPAIGN_REPLIED = "campaign_replied"
    DEAL_CREATED = "deal_created"
    DEAL_STAGE_CHANGED = "deal_stage_changed"
    NOTE_CREATED = "note_created"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    COMPANY_CREATED = "company_created"
