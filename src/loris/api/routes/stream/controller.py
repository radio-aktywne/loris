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
from loris.api.validator import Validator
from loris.state import State


class DependenciesBuilder:
    """Builder for the dependencies of the controller."""

    async def _build_service(self, state: State) -> Service:
        return Service(
            streaming=state.streaming,
        )

    def build(self) -> dict[str, Provide]:
        return {
            "service": Provide(self._build_service),
        }


class Controller(BaseController):
    """Controller for the stream endpoint."""

    dependencies = DependenciesBuilder().build()

    @handlers.post(
        summary="Request a stream",
        raises=[
            ConflictException,
        ],
    )
    async def stream(
        self,
        service: Service,
        data: Annotated[
            m.StreamRequestData,
            Body(
                description="Data for the request.",
            ),
        ],
    ) -> Response[m.StreamResponseData]:
        """Request a stream."""

        data = Validator(m.StreamRequestData).object(data)

        req = m.StreamRequest(
            data=data,
        )

        try:
            res = await service.stream(req)
        except e.ServiceBusyError as ex:
            raise ConflictException(extra=str(ex)) from ex

        rdata = res.data

        return Response(rdata)
