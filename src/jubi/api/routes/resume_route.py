from fastapi import APIRouter, HTTPException, status
from jubi.core.models.ResumeAnalysis import ResumeAnalysisRequest
from jubi.core.repository.resume_repository import ResumeRepository
from jubi.core.services.resume_service import ResumeService
from google.genai import errors
import requests as req
from jubi.integrations.gemini.llm_client import LLM_Client
from jubi.integrations.notifications import Notifications

router = APIRouter(
    prefix="/resume",
    tags=["resume"],
)


@router.post("/analyze")
def get_resume_analysis(request: ResumeAnalysisRequest):
    notified = True
    try:
        repository = ResumeRepository()
        llm = LLM_Client()
        service = ResumeService(resume_repository=repository, llm_client=llm)
        response = service.analyze_resume(request.job_description)
    except (errors.ClientError, errors.APIError, errors.ServerError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"
        )

    try:
        notify = Notifications()
        notify.analysis_notif(response)
    except req.exceptions.RequestException as e:
        notified = False
    return {"notification_sent": notified, "response": response}
