import requests as req
from pathlib import Path

def getAnalysis(job_desc: Path):
    payload = {"job_description": str(job_desc), "resume_id": 0}
    res = req.get("http://127.0.0.1:8000/resume/analyze", json=payload)
    return res.json()



