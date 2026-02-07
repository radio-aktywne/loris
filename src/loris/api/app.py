from collections.abc import Callable, Sequence
from contextlib import AbstractAsyncContextManager

from litestar import Litestar
from litestar.channels import ChannelsPlugin
from litestar.channels.backends.memory import MemoryChannelsBackend
from litestar.openapi import OpenAPIConfig
from litestar.plugins import PluginProtocol
from pylocks.asyncio import AsyncioLock
from pystores.memory import MemoryStore

from loris.api.lifespans import TestLifespan
from loris.api.openapi import OpenAPIConfigBuilder
from loris.api.plugins.pydantic import PydanticPlugin
from loris.api.routes.router import router
from loris.config.models import Config
from loris.services.streaming.service import StreamingService
from loris.state import State


class AppBuilder:
    """Builds the app.

    Args:
        config: Config object.

    """

    def __init__(self, config: Config) -> None:
        self._config = config

    def _build_lifespan(
        self,
    ) -> Sequence[Callable[[Litestar], AbstractAsyncContextManager]]:
        return [
            TestLifespan,
        ]

    def _build_openapi_config(self) -> OpenAPIConfig:
        return OpenAPIConfigBuilder().build()

    def _build_plugins(self) -> Sequence[PluginProtocol]:
        return [
            ChannelsPlugin(backend=MemoryChannelsBackend(), channels=["events"]),
            PydanticPlugin(),
        ]

    def _build_initial_state(self) -> State:
        return State(
            {
                "config": self._config,
                "streaming": StreamingService(
                    config=self._config,
                    store=MemoryStore(set[int]()),
                    lock=AsyncioLock(),
                ),
            }
        )

    def build(self) -> Litestar:
        """Build the app."""
        return Litestar(
            route_handlers=[router],
            debug=self._config.debug,
            lifespan=self._build_lifespan(),
            openapi_config=self._build_openapi_config(),
            plugins=self._build_plugins(),
            state=self._build_initial_state(),
        )
