from collections.abc import Mapping
from typing import Annotated

from litestar import Controller as BaseController
from litestar import handlers
from litestar.di import Provide
from litestar.params import Body
from litestar.response import Response

from loris.api.exceptions import ConflictException
from loris.api.routes.stream import errors as e
from loris.api.routes.stream import models as m
from loris.api.routes.stream.service import Service
from loris.models.base import Serializable
from loris.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(streaming=state.streaming)

    def build(self) -> Mapping[str, Provide]:
        """Build the dependencies."""
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the stream endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.post(
        summary="Request a stream",
        raises=[ConflictException],
    )
    async def stream(
        self,
        service: Service,
        data: Annotated[
            Serializable[m.StreamInput],
            Body(
                description="Data for requesting a stream.",
            ),
        ],
    ) -> Response[Serializable[m.StreamDetails]]:
        """Request a stream."""
        request = m.StreamRequest(data=data.root)

        try:
            response = await service.stream(request)
        except e.ServiceBusyError as ex:
            raise ConflictException from ex

        return Response(Serializable(response.details))
