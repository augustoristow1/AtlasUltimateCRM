class AtlasError(Exception):
    """Base exception for Atlas Ultimate CRM."""


class NotFoundError(AtlasError):
    def __init__(self, entity: str, id: str):
        super().__init__(f"{entity} with id={id} not found")


class ValidationError(AtlasError):
    pass


class MessagingError(AtlasError):
    pass


class PolicyViolationError(AtlasError):
    pass
