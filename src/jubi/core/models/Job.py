from pydantic import BaseModel
from enum import StrEnum
from datetime import datetime


class JobStatus(StrEnum):
    APPLIED = "applied"
    REJECTED = "rejected"
    INTERVIEW = "interview"
    GHOSTED = "ghosted"
    WITHDRAWN = "withdrawn"
    OA = "online assessment"
    OFFER = "offer"


class Job(BaseModel):
    name: str
    company: str
    date_applied: datetime
    status: JobStatus = JobStatus.APPLIED

    @staticmethod
    def convert(status: str) -> JobStatus | None:
        conversion_table = {
            "applied": JobStatus.APPLIED,
            "rejected": JobStatus.REJECTED,
            "interview": JobStatus.INTERVIEW,
            "offer": JobStatus.OFFER,
            "ghosted": JobStatus.GHOSTED,
            "withdrawn": JobStatus.WITHDRAWN,
            "online assessment": JobStatus.OA,
        }

        return conversion_table.get(status)
