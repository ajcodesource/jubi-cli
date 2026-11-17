from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from jubi.core.models.ResumeAnalysis import ResumeAnalysisRequest
from jubi.core.repository.resume_repository import ResumeRepository
from jubi.core.services.resume_service import ResumeService
from google.genai import errors
import requests as req
from jubi.exceptions.exceptions import (
    JobDescriptionError,
    ResumeAccessError,
    ResumeUploadError,
)
from jubi.integrations.gemini.llm_client import LLM_Client
from jubi.integrations.notifications import Notifications

router = APIRouter(
    prefix="/resume",
    tags=["resume"],
)


@router.post("/upload")
def upload_resume(resume_path: str):
    try:
        repository = ResumeRepository()
        llm = LLM_Client()
        service = ResumeService(repository, llm)
        service.upload_resume(Path(resume_path))
        return {"success": True, "message": "Resume successfully uploaded"}
    except (ResumeAccessError, ResumeUploadError, JobDescriptionError) as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "An unexpected server error occurred. Please try again later.",
            },
        )


@router.get("/")
def get_resumes():
    try:
        repo = ResumeRepository()
        llm = LLM_Client()
        service = ResumeService(repo, llm)
        resumes = [Path(resume).name for resume in service.get_resumes()]
        if not resumes:
            raise HTTPException(status_code=404, detail="resumes not found")
        return {"success": True, "resumes": resumes}
    except ResumeUploadError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "resumes": [],
                "success": False,
                "message": "An unexpected server error occurred. Please try again later.",
            },
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
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "An unexpected server error occurred. Please try again later.",
            },
        )

    try:
        notify = Notifications()
        notify.analysis_notif(response)
    except req.exceptions.RequestException as e:
        notified = False
    return {"notification_sent": notified, "response": response}
