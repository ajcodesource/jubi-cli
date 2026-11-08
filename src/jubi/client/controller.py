import requests as req
from pathlib import Path
from jubi.core.models.Job import Job
from jubi.integrations.exceptions import JobValidationError
from jubi.core.services.resume_service import get_job_description


def getAnalysis(job_desc: Path):

    payload = {"job_description": get_job_description(job_desc), "resume_id": 0}
    res = req.get("http://127.0.0.1:8000/resume/analyze", json=payload)
    return res.json()


def postJob(name, company, date, status):
    normalized_job_status = Job.convert(status)
    if normalized_job_status is None:
        raise JobValidationError("Status Invalid")

    validated_model = Job(
        name=name, company=company, date_applied=date, status=normalized_job_status
    )

    payload = validated_model.model_dump(mode="json")
    res = req.post("http://127.0.0.1:8000/jobs/", json=payload)
    res.raise_for_status()
    return res
