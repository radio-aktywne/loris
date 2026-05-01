from math import ceil
from socket import gethostbyname

from pystreams.base import Stream
from pystreams.gstreamer import GStreamerNode, GStreamerStreamMetadata
from pystreams.process import ProcessBasedStreamFactory, ProcessBasedStreamMetadata

from loris.config.models import Config
from loris.services.streaming import models as m


class Runner:
    """Utility class for building and running a stream."""

    def __init__(self, config: Config, stun: m.STUN) -> None:
        self._config = config
        self._stun = stun

    def _build_input_node(self, request: m.StreamRequest) -> GStreamerNode:
        codecs = {m.Codec.OPUS: "OPUS"}

        return GStreamerNode(
            element="customwhipserversrc",
            properties={
                "address": f"http://{self._config.server.host}:{self._config.server.ports.whip}",
                "stun": f"stun://{request.webrtc.stun.host}:{request.webrtc.stun.port}"
                if request.webrtc.stun
                else f"stun://{self._stun.host}:{self._stun.port}",
                "min": self._config.server.ports.rtp,
                "max": self._config.server.ports.rtp,
                "codec": codecs[request.codec],
            },
        )

    def _build_watchdog_node(self) -> GStreamerNode:
        return GStreamerNode(
            element="watchdog",
            properties={
                "timeout": ceil(self._config.streaming.timeout.total_seconds() * 1000)
            },
        )

    def _build_extractor_node(self, request: m.StreamRequest) -> GStreamerNode:
        match request.codec:
            case m.Codec.OPUS:
                return GStreamerNode(element="rtpopusdepay")

    def _build_parser_node(self, request: m.StreamRequest) -> GStreamerNode:
        match request.codec:
            case m.Codec.OPUS:
                return GStreamerNode(element="opusparse")

    def _build_muxer_node(self, request: m.StreamRequest) -> GStreamerNode:
        match request.format:
            case m.Format.OGG:
                return GStreamerNode(element="oggmux")

    def _build_output_node(self, request: m.StreamRequest) -> GStreamerNode:
        return GStreamerNode(
            element="srtsink",
            properties={
                "mode": "caller",
                "uri": f"srt://{gethostbyname(request.srt.host)}:{request.srt.port}",
                **(
                    {"passphrase": request.srt.password} if request.srt.password else {}
                ),
            },
        )

    def _build_stream_metadata(
        self, request: m.StreamRequest
    ) -> GStreamerStreamMetadata:
        return GStreamerStreamMetadata(
            nodes=[
                self._build_input_node(request),
                self._build_watchdog_node(),
                self._build_extractor_node(request),
                self._build_parser_node(request),
                self._build_muxer_node(request),
                self._build_output_node(request),
            ],
        )

    async def _run_stream(self, metadata: ProcessBasedStreamMetadata) -> Stream:
        return await ProcessBasedStreamFactory().create(metadata)

    async def run(self, request: m.StreamRequest) -> Stream:
        """Run the stream."""
        metadata = self._build_stream_metadata(request)
        return await self._run_stream(metadata)
