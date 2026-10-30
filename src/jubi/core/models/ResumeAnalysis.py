from pydantic import BaseModel, Field


class ResumeModelResponse(BaseModel):
    match_percent: str = Field(
        description="Percent match resume alignment with job description "
    )
    apply: bool = Field(
        description="Model's judgement of whether user should apply for this role"
    )
    analysis: str = Field(description="What the model thinks of the resume")
