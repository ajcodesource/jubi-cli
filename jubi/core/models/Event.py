from pydantic import BaseModel
from enum import StrEnum as Enum

class EventType(Enum):
    REJECTED = "rejected"
    INTERVIEW = "interview"

class Event(BaseModel):
    name: EventType
