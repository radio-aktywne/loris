from litestar import Router

from loris.api.routes.sse.controller import Controller

router = Router(
    path="/sse",
    tags=["SSE"],
    route_handlers=[
        Controller,
    ],
)
