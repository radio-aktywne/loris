from typing import Literal

from pydantic import Field

from loris.models.base import SerializableModel
from loris.models.events.enums import EventType
from loris.models.events.fields import CreatedAtField, DataField, TypeField
from loris.utils.time import naiveutcnow


class TestEventData(SerializableModel):
    """Data of a test event."""

    message: str
    """Message of the test event."""


class TestEvent(SerializableModel):
    """Event that is emitted for testing purposes."""

    type: TypeField[Literal[EventType.TEST]] = EventType.TEST
    created_at: CreatedAtField = Field(default_factory=naiveutcnow)
    data: DataField[TestEventData]
