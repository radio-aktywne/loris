from collections.abc import Sequence
from datetime import timedelta

from pydantic import BaseModel, Field

from loris.config.base import BaseConfig
from loris.utils.time import Timedelta


class ServerPortsConfig(BaseModel):
    """Configuration for the server ports."""

    http: int = Field(default=10400, ge=0, le=65535)
    """Port to listen for HTTP requests on."""

    rtp: int = Field(default=10402, ge=0, le=65535)
    """Port to listen for RTP connections on."""

    whip: int = Field(default=10401, ge=0, le=65535)
    """Port to listen for WHIP requests on."""


class ServerConfig(BaseModel):
    """Configuration for the server."""

    host: str = "0.0.0.0"
    """Host to run the server on."""

    ports: ServerPortsConfig = ServerPortsConfig()
    """Configuration for the server ports."""

    trusted: str | Sequence[str] | None = "*"
    """Trusted IP addresses."""


class STUNConfig(BaseModel):
    """Configuration for the STUN server."""

    host: str = "stun.l.google.com"
    """Host of the STUN server."""

    port: int = Field(default=19302, ge=1, le=65535)
    """Port of the STUN server."""


class StreamingConfig(BaseModel):
    """Configuration for the streaming service."""

    stun: STUNConfig = STUNConfig()
    """Configuration for the STUN server."""

    timeout: Timedelta = Field(default=timedelta(minutes=1), ge=timedelta())
    """Time after which a stream will be stopped if no connections are made."""


class Config(BaseConfig):
    """Configuration for the service."""

    debug: bool = True
    """Enable debug mode."""

    server: ServerConfig = ServerConfig()
    """Configuration for the server."""

    streaming: StreamingConfig = StreamingConfig()
    """Configuration for the streaming service."""
