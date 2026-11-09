from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from jubi.core.services import job_service, notification_service
from jubi.core.models.Job import Job
from psycopg import Error
from jubi.integrations.exceptions import (
    JobDeletionError,
    JobRetrievalError,
    JobUpdateError,
    JobWriteError,
    JobValidationError,
    NotificationError,
)

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
)


@router.get("/")
def jobs():
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
    except JobRetrievalError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "jobs": [],
                "success": False,
                "message": "An unexpected server error occurred. Please try again later.",
            },
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
def add_job(job: Job):
    notified = True
    try:
        job_service.add_job(job.name, job.company, job.date_applied, job.status)

    except JobWriteError as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "posted_job": None,
                "notification_sent": False,
                "success": False,
                "message": "An unexpected server error occurred. Please try again later.",
            },
        )
    except JobValidationError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "posted_job": None,
                "notification_sent": False,
                "success": False,
                "message": "An unexpected server error occurred. Please try again later.",
            },
        )

    try:
        notification_service.send_add_notification(job.name, job.company)

    except NotificationError as e:
        notified = False

    return {
        "posted_job": job,
        "notification_sent": notified,
        "success": True,
        "message": "Job successfully added.",
    }


@router.delete("/", status_code=status.HTTP_200_OK)
def delete_job(job_id: int):

    try: 
        deleted_count = job_service.delete_job_from_db(job_id)
        if deleted_count != 0:
            return {"job_id": job_id, "deleted": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
            )

    except JobDeletionError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "An unexpected server error occurred. Please try again later.",
            },
        )


@router.patch("/", status_code=status.HTTP_200_OK)
def update_job_status(job_id: int, new_status: str):
    try:
        rows = job_service.update_status(job_id, new_status)
        if rows != 0:
            return {"job_id": job_id, "new status": new_status, "updated": True}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
            )
    except JobUpdateError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "updated job": False,
                "success": False,
                "message": "An unexpected server error occurred. Please try again later.",
            },
        )
    except JobValidationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Validation error"
        )
