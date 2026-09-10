from pydantic import BaseModel
from enum import StrEnum as Enum

class EventType(Enum):
    REJECTED = "rejected"
    UPDATE = "update"

class Event(BaseModel):
    name: EventType
