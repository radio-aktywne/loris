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

    async def _free(self) -> None:
        async with self._lock:
            await self._store.set(False)

    async def _stop_stream(self, stream: Stream) -> None:
        for action in (stream.terminate, stream.kill):
            with suppress(Exception):
                await asyncio.wait_for(action(), timeout=5)

            with suppress(Exception):
                await asyncio.wait_for(stream.wait(), timeout=5)
                return

    async def _watch_stream(self, stream: Stream) -> None:
        try:
            await stream.wait()
        except asyncio.CancelledError:
            await self._stop_stream(stream)
            raise
        finally:
            await self._free()

    async def _run(self, request: m.StreamRequest) -> None:
        runner = Runner(config=self._config, stun=self._get_default_stun())
        stream = await runner.run(request)

        try:
            await asyncio.wait_for(self._wait_for_stream_start(), 5)
        except BaseException:
            await self._stop_stream(stream)
            raise

        def on_done(task: asyncio.Task) -> None:
            if self._task is task:
                self._task = None

        self._task = asyncio.create_task(self._watch_stream(stream), eager_start=True)
        self._task.add_done_callback(on_done)

    async def stream(self, request: m.StreamRequest) -> m.StreamResponse:
        """Start a stream."""
        await self._reserve()

        try:
            await self._run(request)
        except BaseException:
            await self._free()
            raise

        return m.StreamResponse(stun=request.webrtc.stun or self._get_default_stun())

    async def close(self) -> None:
        """Close gracefully."""
        if self._task is None:
            return

        self._task.cancel()
        with suppress(asyncio.CancelledError):
            await self._task
