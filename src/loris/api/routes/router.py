from litestar import Router

from loris.api.routes.ping.router import router as ping_router
from loris.api.routes.stream.router import router as stream_router

router = Router(
    path="/",
    route_handlers=[
        ping_router,
        stream_router,
    ],
)
