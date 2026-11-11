from collections.abc import Sequence

import uvicorn
from litestar import Litestar
from uvicorn.config import LOGGING_CONFIG

from loris.config.models import ServerConfig


class Server:
    """Server for the application.

    Args:
        app: The application.
        config: The configuration for the server.

    """

    def __init__(self, app: Litestar, config: ServerConfig) -> None:
        self._app = app
        self._config = config

    def run(self) -> None:
        """Run the server."""
        uvicorn.run(
            self._app,
            host=self._config.host,
            port=self._config.ports.http,
            log_config={
                **LOGGING_CONFIG,
                "loggers": {
                    **LOGGING_CONFIG["loggers"],
                    "loris": {
                        "handlers": ["default"],
                        "level": "INFO",
                        "propagate": False,
                    },
                },
            },
            forwarded_allow_ips=list(self._config.trusted)
            if isinstance(self._config.trusted, Sequence)
            else self._config.trusted,
        )
