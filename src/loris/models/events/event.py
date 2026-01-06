from typing import Annotated

from pydantic import Field, RootModel

from loris.models.events import bar as be
from loris.models.events import foo as fe

type Event = Annotated[be.BarEvent | fe.FooEvent, Field(discriminator="type")]
ParsableEvent = RootModel[Event]
