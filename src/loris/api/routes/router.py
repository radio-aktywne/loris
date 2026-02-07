from litestar import Router

from loris.api.routes.ping.router import router as ping_router
from loris.api.routes.sse.router import router as sse_router
from loris.api.routes.stream.router import router as stream_router
from loris.api.routes.test.router import router as test_router

router = Router(
    path="/",
    route_handlers=[
        ping_router,
        sse_router,
        stream_router,
        test_router,
    ],
)
