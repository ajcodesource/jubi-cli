from jubi.core.models.Job import Job, JobStatus
from jubi.core.repository import job_repository
from jubi.utils.notifications import Notifications
from jubi.utils.exceptions import JobWriteError, JobValidationError, NotificationError
from requests.exceptions import RequestException
from sqlite3 import Error as SQLError
import pydantic 

# click.echo("A job has been added to Jubi. A confirmation message has been sent to Discord!")
def add_job(name, company, date, status):
    convert = Job.convert(status)
    if(convert is None):
        raise JobValidationError("Status Incorrect")
    
    validate = None
    try:
        validate = Job(name=name, company=company, date_applied=date, status= convert)

    except pydantic.ValidationError as e:
        raise JobValidationError(f"Job could not be validated {e}")
    
    try:    
        success = job_repository.add_job(validate.name, validate.company, validate.date_applied, validate.status)
        if success:
            try:
                notif = Notifications()
                notif.add_notif(validate.name, validate.company)
        
            except RequestException as r:
                raise NotificationError(f"Notification Failed {r}")
                

        else:
            raise JobWriteError(f"Failed to write job {validate.name} at {validate.company}")
    except SQLError as e:
        raise JobWriteError(f"Failed to write job {e}")

def get_all_jobs(rejection, applied, interview, offer):
    result = job_repository.list_all_jobs(rejection, applied, interview, offer)
    return result


def delete_job_from_db(job_id):
    success = job_repository.delete_job(job_id)
    return success 

def update_status(job_id: int, new_status: str):
    success = job_repository.update_job_status(job_id=job_id, new_status=new_status)
    return success
    

