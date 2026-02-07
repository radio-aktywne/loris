import asyncio
from collections.abc import Set as AbstractSet

from pylocks.base import Lock
from pystores.base import Store
from pystreams.base import Stream

from loris.config.models import Config
from loris.services.streaming import errors as e
from loris.services.streaming import models as m
from loris.services.streaming.runner import Runner


class StreamingService:
    """Service to manage streaming."""

    def __init__(
        self, config: Config, store: Store[AbstractSet[int]], lock: Lock
    ) -> None:
        self._config = config
        self._store = store
        self._lock = lock
        self._tasks = set[asyncio.Task]()

    def _get_default_stun(self) -> m.STUNServer:
        return m.STUNServer(
            host=self._config.streamer.stun.host, port=self._config.streamer.stun.port
        )

    async def _reserve_port(self) -> int:
        async with self._lock:
            used = await self._store.get()
            available = set(self._config.server.ports.whip - used)

            if not available:
                raise e.NoPortsAvailableError

            port = available.pop()

            await self._store.set(used | {port})

        return port

    async def _wait_for_stream_start(self, port: int) -> None:
        host = self._config.server.host

        while True:
            try:
                _, writer = await asyncio.open_connection(host, port)
                writer.close()
                await writer.wait_closed()
            except ConnectionError:
                pass
            else:
                break

    async def _free_port(self, port: int) -> None:
        async with self._lock:
            used = set(await self._store.get())
            used.remove(port)
            await self._store.set(used)

    async def _watch_stream(self, stream: Stream, port: int) -> None:
        try:
            await stream.wait()
        finally:
            await self._free_port(port)

    async def _run(
        self,
        port: int,
        codec: m.Codec,
        fmt: m.Format,
        srt: m.SRTServer,
        stun: m.STUNServer,
    ) -> None:
        runner = Runner(self._config)
        stream = await runner.run(port=port, codec=codec, fmt=fmt, srt=srt, stun=stun)

        await asyncio.wait_for(self._wait_for_stream_start(port), 5)
        task = asyncio.create_task(self._watch_stream(stream, port))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def stream(self, request: m.StreamRequest) -> m.StreamResponse:
        """Start a stream."""
        codec = request.codec
        fmt = request.format
        srt = request.srt
        stun = request.stun

        port = await self._reserve_port()
        stun = stun or self._get_default_stun()

        try:
            await self._run(port, codec, fmt, srt, stun)
        except Exception:
            await self._free_port(port)
            raise

        return m.StreamResponse(port=port, stun=stun)
