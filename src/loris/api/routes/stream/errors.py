class ServiceError(Exception):
    """Base class for service errors."""


class ValidationError(ServiceError):
    """Raised when a validation error occurs."""


class ConflictError(ValidationError):
    """Raised when a conflict error occurs."""
