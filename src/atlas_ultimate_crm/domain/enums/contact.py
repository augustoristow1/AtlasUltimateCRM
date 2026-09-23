from enum import Enum


class LifecycleStage(str, Enum):
    LEAD = "lead"
    PROSPECT = "prospect"
    QUALIFIED = "qualified"
    CUSTOMER = "customer"
    CHURNED = "churned"


class ContactSource(str, Enum):
    MANUAL = "manual"
    CSV_IMPORT = "csv_import"
    CAMPAIGN = "campaign"
    WHATSAPP_INBOUND = "whatsapp_inbound"
    API = "api"


class OptInStatus(str, Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    PENDING = "pending"
