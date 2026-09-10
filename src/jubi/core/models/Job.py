from pydantic import BaseModel
from enum import StrEnum
from jubi.core.models.Event import Event as JobEvent
from datetime import datetime


class JobStatus(StrEnum):
    APPLIED = "applied"
    REJECTED = "rejected"
    INTERVIEW = "interview"
    OFFER = "offer"

class Job(BaseModel):
    name: str
    company: str
    date_applied: datetime | None = None
    status: JobStatus = JobStatus.APPLIED

    def update(self, event: JobEvent):
        if(event.name == "rejected"):
            self.status = JobStatus.REJECTED
        if(event.name == "update"):
            match self.status:
                case JobStatus.APPLIED:
                    self.status = JobStatus.INTERVIEW
                case JobStatus.INTERVIEW:
                    self.status = JobStatus.OFFER
                case _:
                    self.status = JobStatus.APPLIED
    @staticmethod
    def convert(status: str) -> JobStatus | None:
        hashmap = {
            "applied": JobStatus.APPLIED,
            "rejected": JobStatus.REJECTED,
            "interview": JobStatus.INTERVIEW,
            "offer": JobStatus.OFFER
        }

        return hashmap.get(status)






