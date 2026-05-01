import asyncio

from pylocks.base import Lock
from pystores.base import Store
from pystreams.base import Stream

from loris.config.models import Config
from loris.services.streaming import errors as e
from loris.services.streaming import models as m
from loris.services.streaming.runner import Runner


class StreamingService:
    """Service to manage streaming."""

    def __init__(self, config: Config, store: Store[bool], lock: Lock) -> None:
        self._config = config
        self._store = store
        self._lock = lock
        self._tasks = set[asyncio.Task]()

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

    async def _watch_stream(self, stream: Stream) -> None:
        try:
            await stream.wait()
        finally:
            await self._free()

    async def _run(self, request: m.StreamRequest) -> None:
        runner = Runner(config=self._config, stun=self._get_default_stun())
        stream = await runner.run(request)

        await asyncio.wait_for(self._wait_for_stream_start(), 5)
        task = asyncio.create_task(self._watch_stream(stream))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def stream(self, request: m.StreamRequest) -> m.StreamResponse:
        """Start a stream."""
        await self._reserve()

        try:
            await self._run(request)
        except Exception:
            await self._free()
            raise

        return m.StreamResponse(stun=request.webrtc.stun or self._get_default_stun())
