from pydantic import BaseModel
from enum import StrEnum
from jubi.core.models.Event import Event as JobEvent


class JobStatus(StrEnum):
    APPLIED = "applied"
    REJECTED = "rejected"
    INTERVIEW = "interview"
    OFFER = "offer"

class Job(BaseModel):
    name: str
    company: str
    date_applied: str | None = None
    status: JobStatus = JobStatus.APPLIED

    def on_event(self, event: JobEvent):
        if(event.name == "REJECT"):
            self.status = JobStatus.REJECTED
        if(event.name == "UPDATE"):
            match self.status:
                case JobStatus.APPLIED:
                    self.status = JobStatus.INTERVIEW
                case JobStatus.INTERVIEW:
                    self.status = JobStatus.OFFER
                case _:
                    self.status = JobStatus.APPLIED






