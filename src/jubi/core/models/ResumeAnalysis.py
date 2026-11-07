from pydantic import BaseModel, Field
from pathlib import Path


class ResumeModelResponse(BaseModel):
    match_percent: str = Field(
        description="Percent match resume alignment with job description "
    )
    apply: bool = Field(
        description="Model's judgement of whether user should apply for this role"
    )
    analysis: str = Field(description="What the model thinks of the resume")


class ResumeAnalysisRequest(BaseModel):
    job_description: Path = Field(description="Path to file containing job description")
    resume_id: int | None = None
