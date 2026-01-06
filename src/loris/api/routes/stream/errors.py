class ServiceError(Exception):
    """Base class for service errors."""


class ServiceBusyError(ServiceError):
    """Raised when the service is busy."""
