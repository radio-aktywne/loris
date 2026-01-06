from collections.abc import AsyncIterator

from loris.models.base import datamodel


@datamodel
class SubscribeRequest:
    """Request to subscribe."""


@datamodel
class SubscribeResponse:
    """Response for subscribe."""

    messages: AsyncIterator[str]
    """Stream of messages."""
