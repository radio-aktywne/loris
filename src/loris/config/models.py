from collections.abc import Sequence
from collections.abc import Set as AbstractSet
from datetime import timedelta
from typing import Annotated, Any, Self

from pydantic import BaseModel, Field, field_validator, model_validator

from loris.config.base import BaseConfig


class ServerRTPPortsConfig(BaseModel):
    """Configuration for the server RTP ports."""

    max: int = Field(default=10402, ge=1, le=65535)
    """Maximum port to select from when listening for RTP connections."""

    min: int = Field(default=10402, ge=1, le=65535)
    """Minimum port to select from when listening for RTP connections."""

    @model_validator(mode="after")
    def validate_ports(self) -> Self:
        """Validate ports."""
        if self.min > self.max:
            message = "Minimum port cannot be greater than maximum port."
            raise ValueError(message)

        return self


class ServerPortsConfig(BaseModel):
    """Configuration for the server ports."""

    http: int = Field(default=10400, ge=0, le=65535)
    """Port to listen for HTTP requests on."""

    rtp: ServerRTPPortsConfig = ServerRTPPortsConfig()
    """Configuration for the server RTP ports."""

    whip: AbstractSet[Annotated[int, Field(ge=1, le=65535)]] = Field(
        default=frozenset({10401}), min_length=1
    )
    """Ports to select from when listening for WHIP requests."""

    @field_validator("whip", mode="before")
    @classmethod
    def validate_whip(cls, v: Any) -> Any:
        """Validate WHIP ports."""
        if isinstance(v, int):
            v = {v}
        elif isinstance(v, str):
            v = set(v.split(","))

        return v


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

    port: int = Field(default=19302, ge=0, le=65535)
    """Port of the STUN server."""


class StreamerConfig(BaseModel):
    """Configuration for the streamer."""

    stun: STUNConfig = STUNConfig()
    """Configuration for the STUN server."""

    timeout: timedelta = Field(default=timedelta(minutes=1), ge=0)
    """Time after which a stream will be stopped if no connections are made."""


class Config(BaseConfig):
    """Configuration for the service."""

    debug: bool = True
    """Enable debug mode."""

    server: ServerConfig = ServerConfig()
    """Configuration for the server."""

    streamer: StreamerConfig = StreamerConfig()
    """Configuration for the streamer."""
