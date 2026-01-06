from litestar import Router

from loris.api.routes.stream.controller import Controller

router = Router(
    path="/stream",
    tags=["Stream"],
    route_handlers=[
        Controller,
    ],
)
