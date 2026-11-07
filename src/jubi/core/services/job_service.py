from jubi.core.models.Job import Job
from jubi.core.repository import job_repository
from jubi.integrations.notifications import Notifications
from jubi.integrations.exceptions import (
    JobWriteError,
    JobValidationError,
    NotificationError,
)
from requests.exceptions import RequestException
from psycopg import Error as PGError
import pydantic


# click.echo("A job has been added to Jubi. A confirmation message has been sent to Discord!")
def add_job(name, company, date, status):
    try:
        normalized_job_status = Job.convert(status)
        if normalized_job_status is None:
            raise JobValidationError("Status Invalid")

        validated_model = Job(
            name=name, company=company, date_applied=date, status=normalized_job_status
        )
        job_repository.add_job(
            validated_model.name,
            validated_model.company,
            validated_model.date_applied,
            validated_model.status,
        )

    except pydantic.ValidationError as e:
        raise JobValidationError(f"Job could not be validated {e}")
    except PGError as e:
        raise JobWriteError(f"Failed to write job {e}")


def get_all_jobs(status):
    result = job_repository.list_all_jobs(status)
    return result


def delete_job_from_db(job_id: int):
    success = job_repository.delete_job(job_id)
    return success


def update_status(job_id: int, new_status: str):
    convert_status = Job.convert(new_status)
    if convert_status is None:
        raise JobValidationError("status is invalid")

    success = job_repository.update_job_status(job_id=job_id, new_status=new_status)
    return success
