from pydantic import BaseModel
from enum import StrEnum
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

    @staticmethod
    def convert(status: str) -> JobStatus | None:
        hashmap = {
            "applied": JobStatus.APPLIED,
            "rejected": JobStatus.REJECTED,
            "interview": JobStatus.INTERVIEW,
            "offer": JobStatus.OFFER
        }

        return hashmap.get(status)






