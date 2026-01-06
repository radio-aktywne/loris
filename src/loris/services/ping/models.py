from loris.models.base import datamodel


@datamodel
class PingRequest:
    """Request to ping."""


@datamodel
class PingResponse:
    """Response for ping."""
