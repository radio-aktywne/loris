from litestar import Controller as BaseController
from litestar import handlers
from litestar.datastructures import CacheControlHeader
from litestar.di import Provide
from litestar.response import Response
from litestar.status_codes import HTTP_204_NO_CONTENT

from emipass.api.routes.ping import models as m
from emipass.api.routes.ping.service import Service


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self) -> Service:
        return Service()

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the ping endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.get(
        summary="Ping",
        description="Do nothing.",
        cache_control=CacheControlHeader(no_store=True),
        status_code=HTTP_204_NO_CONTENT,
    )
    async def ping(self, service: Service) -> Response[None]:
        req = m.PingRequest()
        await service.ping(req)
        return Response(None)
