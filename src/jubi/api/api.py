from fastapi import FastAPI, status
from jubi.core.services import job_controller
from jubi.core.models.Job import Job


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to Jubi"}


@app.get("/jobs/")
async def jobs(rejected: bool = False, 
                applied: bool = False,
                interview: bool = False, 
                 offer: bool = False):
    result = job_controller.get_all_jobs(rejected, applied, interview, offer)
    if(result == []):
        return []
    else:
        return [Job(name=row[1], company=row[2], date_applied=row[3], status=row[4]) for row in result]

@app.post("/jobs/", status_code=status.HTTP_201_CREATED)
async def add_job(job: Job):
    job_controller.add_job(job.name, job.company, job.date_applied, job.status)
    return job

@app.delete("/jobs/delete/{job_id}", status_code=status.HTTP_200_OK)
async def delete_job(job_id: int):
    job_controller.delete_job_from_db(job_id)
    return {"job_id": job_id}

@app.patch("/jobs/update/{job_id}/", status_code=status.HTTP_200_OK)
async def update_job_status(job_id: int, new_status:str):
    job_controller.update_status(job_id, new_status)
    return {"job_id": job_id, "new status": new_status}


