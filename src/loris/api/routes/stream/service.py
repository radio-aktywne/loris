from collections.abc import Generator
from contextlib import contextmanager

from loris.api.routes.stream import errors as e
from loris.api.routes.stream import models as m
from loris.services.streaming import errors as se
from loris.services.streaming.service import StreamingService


class Service:
    """Service for the stream endpoint."""

    def __init__(self, streaming: StreamingService) -> None:
        self._streaming = streaming

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except se.StreamBusyError as ex:
            raise e.ConflictError from ex
        except se.ServiceError as ex:
            raise e.ServiceError from ex

    async def stream(self, request: m.StreamRequest) -> m.StreamResponse:
        """Start a stream."""
        stream_request = request.data.map()

        with self._handle_errors():
            stream_response = await self._streaming.stream(stream_request)

        return m.StreamResponse(details=m.StreamDetails.map(stream_response))
