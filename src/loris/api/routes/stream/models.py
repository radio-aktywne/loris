from typing import Annotated

from pydantic import Field

from loris.models.base import SerializableModel, datamodel, serializable
from loris.services.streaming import models as sm


@serializable
@datamodel
class SRTServer(sm.SRTServer):
    """SRT server configuration."""

    password: str | None = None
    """Password to authenticate with the SRT server."""

    def map(self) -> sm.SRTServer:
        """Map to external representation."""
        return sm.SRTServer(**vars(self))


@serializable
@datamodel
class STUNServer(sm.STUNServer):
    """STUN server configuration."""

    @staticmethod
    def rmap(stun: sm.STUNServer) -> "STUNServer":
        """Map to internal representation."""
        return STUNServer(**vars(stun))

    def map(self) -> sm.STUNServer:
        """Map to external representation."""
        return sm.STUNServer(**vars(self))


class StreamRequestData(SerializableModel):
    """Data for a stream request."""

    codec: sm.Codec = sm.Codec.OPUS
    """Audio codec."""

    format: sm.Format = sm.Format.OGG
    """Audio format."""

    srt: SRTServer
    """SRT server configuration."""

    stun: STUNServer | None = None
    """STUN server configuration."""


class StreamResponseData(SerializableModel):
    """Data for a stream response."""

    stun: STUNServer
    """STUN server configuration."""

    port: Annotated[int, Field(ge=1, le=65535)]
    """Port to stream to."""


@datamodel
class StreamRequest:
    """Request to stream."""

    data: StreamRequestData
    """Data for the request."""


@datamodel
class StreamResponse:
    """Response for stream."""

    data: StreamResponseData
    """Data for the response."""
