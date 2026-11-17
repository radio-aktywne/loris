import asyncio
from contextlib import suppress

from pylocks.base import Lock
from pystores.base import Store
from pystreams.base import Stream

from loris.config.models import Config
from loris.services.streaming import errors as e, models as m
from loris.services.streaming.runner import Runner


class StreamingService:
    """Service to manage streaming."""

    def __init__(self, config: Config, store: Store[bool], lock: Lock) -> None:
        self._config = config
        self._store = store
        self._lock = lock
        self._task: asyncio.Task | None = None
        self._transition = asyncio.Lock()

    def _get_default_stun(self) -> m.STUN:
        return m.STUN(
            host=self._config.streaming.stun.host, port=self._config.streaming.stun.port
        )

    async def _reserve(self) -> None:
        async with self._lock:
            busy = await self._store.get()

            if busy:
                raise e.StreamBusyError

            await self._store.set(True)

    async def _wait_for_stream_start(self) -> None:
        host = self._config.server.host
        port = self._config.server.ports.whip

        while True:
            try:
                _, writer = await asyncio.open_connection(host, port)
                writer.close()
                await writer.wait_closed()
            except ConnectionError:
                pass
            else:
                break

    async def _release(self) -> None:
        async with self._lock:
            await self._store.set(False)

    async def _stop_stream(self, stream: Stream) -> None:
        for action in (stream.terminate, stream.kill):
            with suppress(Exception):
                await asyncio.wait_for(action(), timeout=5)

            with suppress(Exception):
                await asyncio.wait_for(stream.wait(), timeout=5)
                return

        raise e.StreamStopError

    async def _watch_stream(self, stream: Stream) -> None:
        try:
            await stream.wait()
            await self._release()
        except asyncio.CancelledError:
            await self._stop_stream(stream)
            await self._release()

    async def _stop(self) -> None:
        if self._task is None:
            return

        self._task.cancel()

        try:
            await asyncio.shield(self._task)
        except asyncio.CancelledError:
            while not self._task.done():
                with suppress(asyncio.CancelledError):
                    await asyncio.shield(self._task)

            await self._task
            raise

        self._task = None

    async def _run(self, request: m.StreamRequest) -> None:
        runner = Runner(config=self._config, stun=self._get_default_stun())
        stream = await runner.run(request)

        self._task = asyncio.create_task(self._watch_stream(stream), eager_start=True)

        try:
            await asyncio.wait_for(self._wait_for_stream_start(), 5)
        except BaseException:
            await self._stop()
            raise

    async def stream(self, request: m.StreamRequest) -> m.StreamResponse:
        """Start a stream."""
        async with self._transition:
            if request.force:
                await self._stop()

            await self._reserve()

            try:
                await self._run(request)
            except e.StreamStopError:
                raise
            except BaseException:
                await self._release()
                raise

        return m.StreamResponse(stun=request.webrtc.stun or self._get_default_stun())

    async def close(self) -> None:
        """Close gracefully."""
        async with self._transition:
            with suppress(asyncio.CancelledError, RuntimeError):
                await self._stop()

            self._task = None
