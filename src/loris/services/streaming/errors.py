class ServiceError(Exception):
    """Base class for service errors."""


class StreamBusyError(ServiceError):
    """Raised when another stream is already being handled at the moment."""

    def __init__(self) -> None:
        super().__init__("Another stream is already being handled.")


class StreamStopError(ServiceError):
    """Raised when the stream cannot be stopped."""

    def __init__(self) -> None:
        super().__init__("Failed to stop the stream.")
