from enum import StrEnum

from loris.models.base import datamodel


class Codec(StrEnum):
    """Audio codec."""

    OPUS = "opus"


class Format(StrEnum):
    """Audio format."""

    OGG = "ogg"


@datamodel
class STUN:
    """STUN configuration."""

    host: str
    """Host of the STUN server."""

    port: int
    """Port of the STUN server."""


@datamodel
class WebRTC:
    """WebRTC configuration."""

    stun: STUN | None
    """STUN configuration."""


@datamodel
class SRT:
    """SRT configuration."""

    host: str
    """Host of the SRT server."""

    port: int
    """Port of the SRT server."""

    password: str | None
    """Password to authenticate with the SRT server."""


@datamodel
class StreamRequest:
    """Request to stream."""

    bitrate: int
    """Audio bitrate in bits per second."""

    channels: int
    """Number of audio channels."""

    codec: Codec
    """Audio codec."""

    format: Format
    """Audio format."""

    samplerate: int
    """Audio sample rate in Hz."""

    srt: SRT
    """SRT configuration."""

    webrtc: WebRTC
    """WebRTC configuration."""


@datamodel
class StreamResponse:
    """Response for stream."""

    stun: STUN
    """STUN configuration."""
