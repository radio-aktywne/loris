from litestar.datastructures import State as LitestarState

from loris.config.models import Config
from loris.services.streaming.service import StreamingService


class State(LitestarState):
    """Use this class as a type hint for the state of the service."""

    config: Config
    """Configuration for the service."""

    streaming: StreamingService
    """Service to manage streaming."""
