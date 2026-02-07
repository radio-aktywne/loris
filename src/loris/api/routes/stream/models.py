from typing import Annotated, Self

from pydantic import Field

from loris.models.base import SerializableModel, datamodel
from loris.services.streaming import models as sm


class SRTServer(SerializableModel):
    """SRT server configuration."""

    host: str
    """Host of the SRT server."""

    port: int
    """Port of the SRT server."""

    password: str | None = None
    """Password to authenticate with the SRT server."""

    def map(self) -> sm.SRTServer:
        """Map to external representation."""
        return sm.SRTServer(host=self.host, port=self.port, password=self.password)


class STUNServer(SerializableModel):
    """STUN server configuration."""

    host: str
    """Host of the STUN server."""

    port: int
    """Port of the STUN server."""

    @classmethod
    def imap(cls, stun: sm.STUNServer) -> Self:
        """Map to internal representation."""
        return cls(host=stun.host, port=stun.port)

    def emap(self) -> sm.STUNServer:
        """Map to external representation."""
        return sm.STUNServer(host=self.host, port=self.port)


class StreamInput(SerializableModel):
    """Data for requesting a stream."""

    codec: sm.Codec = sm.Codec.OPUS
    """Audio codec."""

    format: sm.Format = sm.Format.OGG
    """Audio format."""

    srt: SRTServer
    """SRT server configuration."""

    stun: STUNServer | None = None
    """STUN server configuration."""


class StreamDetails(SerializableModel):
    """Details of the stream."""

    stun: STUNServer
    """STUN server configuration."""

    port: Annotated[int, Field(ge=1, le=65535)]
    """Port to stream to."""


type StreamRequestData = StreamInput

type StreamResponseDetails = StreamDetails


@datamodel
class StreamRequest:
    """Request to stream."""

    data: StreamRequestData
    """Data for requesting a stream."""


@datamodel
class StreamResponse:
    """Response for stream."""

    details: StreamResponseDetails
    """Details of the stream."""
