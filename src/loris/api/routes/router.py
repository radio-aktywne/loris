from litestar import Router

from loris.api.routes.ping.router import router as ping
from loris.api.routes.sse.router import router as sse
from loris.api.routes.stream.router import router as stream
from loris.api.routes.test.router import router as test

router = Router(
    path="/",
    route_handlers=[
        ping,
        sse,
        stream,
        test,
    ],
)
