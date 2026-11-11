import asyncio
import logging
from time import monotonic
from typing import IO, override
from uuid import UUID, uuid4

from pystreams.base import Stream, StreamFactory
from pystreams.process import (
    ProcessBasedStream,
    ProcessBasedStreamFactory,
    ProcessBasedStreamMetadata,
)


logger = logging.getLogger(__name__)


class LoggedStream(Stream):
    """Stream with logging."""

    def __init__(self, stream: ProcessBasedStream, sid: UUID) -> None:
        self._stream = stream
        self._sid = sid
        self._started = monotonic()
        self._stopping = False
        self._task = asyncio.create_task(self._watch())

    async def _read(self, reader: asyncio.StreamReader | None, channel: str) -> None:
        if reader is None:
            return

        while True:
            try:
                line = await reader.readline()

                if not line:
                    break

                text = line.decode(errors="replace").rstrip()
            except ValueError:
                logger.warning("[%s] [%s] Failed to read output", self._sid, channel)
                continue

            logger.info("[%s] [%s] %s", self._sid, channel, text)

    async def _watch(self) -> None:
        await asyncio.gather(
            self._read(self._stream.process.stdout, "stdout"),
            self._read(self._stream.process.stderr, "stderr"),
            self._stream.wait(),
        )

        code = self._stream.process.returncode
        duration = monotonic() - self._started

        if code == 0 or self._stopping:
            logger.info(
                "Stream ended (id=%s, code=%s, duration=%.1fs)",
                self._sid,
                code,
                duration,
            )
        else:
            logger.warning(
                "Stream ended unexpectedly (id=%s, code=%s, duration=%.1fs)",
                self._sid,
                code,
                duration,
            )

    @override
    async def terminate(self) -> None:
        await self._stream.terminate()
        self._stopping = True
        logger.info("Stopping stream (id=%s)", self._sid)

    @override
    async def kill(self) -> None:
        await self._stream.kill()
        self._stopping = True
        logger.warning("Killing stream (id=%s)", self._sid)

    @override
    async def wait(self) -> None:
        await asyncio.shield(self._task)


class LoggedStreamFactory(StreamFactory[ProcessBasedStreamMetadata]):
    """Factory for logged streams."""

    @override
    async def create(
        self,
        metadata: ProcessBasedStreamMetadata,
        stdin: IO | int | None = asyncio.subprocess.DEVNULL,
        stdout: IO | int | None = asyncio.subprocess.PIPE,
        stderr: IO | int | None = asyncio.subprocess.PIPE,
    ) -> LoggedStream:
        sid = uuid4()
        logger.info("Starting stream (id=%s)", sid)

        try:
            stream = await ProcessBasedStreamFactory().create(
                metadata, stdin=stdin, stdout=stdout, stderr=stderr
            )
        except Exception:
            logger.exception("Failed to start stream (id=%s)", sid)
            raise

        logger.info("Stream started (id=%s, pid=%s)", sid, stream.process.pid)

        return LoggedStream(stream, sid)
