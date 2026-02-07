from collections.abc import Generator
from contextlib import contextmanager

from loris.api.routes.stream import errors as e
from loris.api.routes.stream import models as m
from loris.services.streaming import errors as se
from loris.services.streaming import models as sm
from loris.services.streaming.service import StreamingService


class Service:
    """Service for the stream endpoint."""

    def __init__(self, streaming: StreamingService) -> None:
        self._streaming = streaming

    @contextmanager
    def _handle_errors(self) -> Generator[None]:
        try:
            yield
        except se.NoPortsAvailableError as ex:
            raise e.ServiceBusyError from ex
        except se.ServiceError as ex:
            raise e.ServiceError from ex

    async def stream(self, request: m.StreamRequest) -> m.StreamResponse:
        """Start a stream."""
        stream_request = sm.StreamRequest(
            codec=request.data.codec,
            format=request.data.format,
            srt=request.data.srt.map(),
            stun=request.data.stun.emap() if request.data.stun else None,
        )

        with self._handle_errors():
            stream_response = await self._streaming.stream(stream_request)

        return m.StreamResponse(
            details=m.StreamDetails(
                stun=m.STUNServer.imap(stream_response.stun), port=stream_response.port
            )
        )
