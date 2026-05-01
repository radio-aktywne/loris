from typing import Annotated, Self

from pydantic import Field

from loris.models.base import SerializableModel, datamodel
from loris.services.streaming import models as sm


class STUN(SerializableModel):
    """STUN configuration."""

    host: str
    """Host of the STUN server."""

    port: Annotated[int, Field(ge=1, le=65535)]
    """Port of the STUN server."""

    @classmethod
    def imap(cls, stun: sm.STUN) -> Self:
        """Map to internal representation."""
        return cls(host=stun.host, port=stun.port)

    def emap(self) -> sm.STUN:
        """Map to external representation."""
        return sm.STUN(host=self.host, port=self.port)


class WebRTC(SerializableModel):
    """WebRTC configuration."""

    stun: STUN | None = None
    """STUN configuration."""

    def emap(self) -> sm.WebRTC:
        """Map to external representation."""
        return sm.WebRTC(
            stun=self.stun.emap() if self.stun else None,
        )


class SRT(SerializableModel):
    """SRT configuration."""

    host: str
    """Host of the SRT server."""

    port: Annotated[int, Field(ge=1, le=65535)]
    """Port of the SRT server."""

    password: str | None = None
    """Password to authenticate with the SRT server."""

    def emap(self) -> sm.SRT:
        """Map to external representation."""
        return sm.SRT(
            host=self.host,
            port=self.port,
            password=self.password,
        )


class StreamInput(SerializableModel):
    """Data for requesting a stream."""

    bitrate: Annotated[int, Field(ge=1)] = 256000
    """Audio bitrate in bits per second."""

    channels: Annotated[int, Field(ge=1)] = 2
    """Number of audio channels."""

    codec: sm.Codec = sm.Codec.OPUS
    """Audio codec."""

    format: sm.Format = sm.Format.OGG
    """Audio format."""

    samplerate: Annotated[int, Field(ge=1)] = 48000
    """Audio sample rate in Hz."""

    srt: SRT
    """SRT configuration."""

    webrtc: WebRTC = WebRTC()
    """WebRTC configuration."""

    def emap(self) -> sm.StreamRequest:
        """Map to external representation."""
        return sm.StreamRequest(
            bitrate=self.bitrate,
            channels=self.channels,
            codec=self.codec,
            format=self.format,
            samplerate=self.samplerate,
            srt=self.srt.emap(),
            webrtc=self.webrtc.emap(),
        )


class StreamDetails(SerializableModel):
    """Details of the stream."""

    stun: STUN
    """STUN configuration."""

    @classmethod
    def imap(cls, details: sm.StreamResponse) -> Self:
        """Map to internal representation."""
        return cls(stun=STUN.imap(details.stun))


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
