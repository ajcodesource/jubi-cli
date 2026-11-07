from fastapi import APIRouter, HTTPException, status
from jubi.core.services import job_service
from jubi.core.models.Job import Job
from psycopg import Error

from jubi.integrations.exceptions import (
    JobValidationError,
    JobWriteError,
    NotificationError,
)

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


@router.get("/")
async def jobs():
    try:
        result = job_service.get_all_jobs([])
        if result == []:
            return []
        else:
            return [
                (
                    row[0],
                    Job(
                        name=row[1], company=row[2], date_applied=row[3], status=row[4]
                    ),
                )
                for row in result
            ]
    except Error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database Error"
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_job(job: Job):
    notified = True
    try:
        job_service.add_job(job.name, job.company, job.date_applied, job.status)

    except (Error, JobWriteError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Write Error {e}"
        )
    except NotificationError as e:
        notified = False
        
    return {"posted_job": job, "notification_sent": notified, "success": True}


@router.delete("/{job_id}", status_code=status.HTTP_200_OK)
async def delete_job(job_id: int):

    try:
        success = job_service.delete_job_from_db(job_id)
        if success:
            return {"job_id": job_id, "deleted": True}
        else:
            return {"job_id": job_id, "deleted": False}

    except JobWriteError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Database Error"
        )


@router.patch("/update/{job_id}/", status_code=status.HTTP_200_OK)
async def update_job_status(job_id: int, new_status: str):
    try:
        success = job_service.update_status(job_id, new_status)
        if success:
            return {"job_id": job_id, "new status": new_status, "updated": True}
        else:
            return {"job_id": job_id, "new status": new_status, "updated": False}
    except Error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database Error"
        )
    except JobValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Validation error"
        )
