from pathlib import Path
from jubi.core.repository.resume_repository import ResumeRepository
from jubi.utils.exceptions import (
    JobDescriptionError,
    NotificationError,
    ResumeAccessError,
    ResumeUploadError,
)
from requests.exceptions import RequestException
from pypdf import PdfReader
from jubi.client.llm_client import LLM_Client
from jubi.utils.notifications import Notifications


def upload_resume(resume: Path):

    try:
        repo = ResumeRepository()
        return repo.add_resume(resume)
    except OSError as e:
        raise ResumeUploadError(f"Failed to upload {e}")


def get_resumes() -> list[Path]:
    try:
        repo = ResumeRepository()
        return repo.get_resumes()
    except OSError as e:
        raise ResumeUploadError(f"Failed to get resume {e}")


def get_job_description(job_file: Path) -> str:
    try:
        return job_file.read_text(encoding="utf-8")
    except FileNotFoundError as e:
        raise JobDescriptionError(f"Job description not found: {job_file}") from e
    except UnicodeDecodeError as e:
        raise JobDescriptionError(f"{job_file} isn't a UTF-8 text file") from e
    except OSError as e:
        raise JobDescriptionError(f"Couldn't read {job_file}: {e.strerror}") from e


###
def analyze_resume(job_file: Path):
    resumes = get_resumes()
    if not resumes:
        raise ResumeAccessError("No resume has been uploaded yet")

    resume = resumes[0]
    reader = PdfReader(resume)

    resume_text: str = ""
    for page in reader.pages:
        resume_text += page.extract_text()

    description = get_job_description(job_file)

    analyzer = LLM_Client()
    response = analyzer.send_prompt(resume_text, description)
    try:
        notify = Notifications()
        notify.analysis_notif(response)
    except RequestException as e:
        raise NotificationError(f"Notification Failed {e}") from e
