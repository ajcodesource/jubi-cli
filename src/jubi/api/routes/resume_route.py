from fastapi import APIRouter, HTTPException, status
from jubi.core.models.ResumeAnalysis import ResumeAnalysisRequest
from jubi.core.services.resume_service import analyze_resume
from google.genai import errors
import requests as req
from jubi.integrations.notifications import Notifications
router = APIRouter(
    prefix="/resume",
    tags=["resume"],
)

@router.get("/analyze")
async def get_resume_analysis(request: ResumeAnalysisRequest):
    notified = True
    try:
       response = analyze_resume(request.job_description)
    except (errors.ClientError, errors.APIError, errors.ServerError) as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")

    try:
        notify = Notifications()
        notify.analysis_notif(response)
    except req.exceptions.RequestException as e:
        notified = False
    return {"notification_sent": notified, "response": response}

        

        
