import click
from requests import ConnectionError, Response
from jubi.client import controller
from jubi.core.models.Job import Job, JobStatus
from jubi.core.repository.resume_repository import ResumeRepository
from jubi.core.services import resume_service
from jubi.exceptions.exceptions import (
    JobDescriptionError,
    JobValidationError,
    NotificationError,
    ResumeAccessError,
    ResumeUploadError,
)
from datetime import datetime, timezone
from pathlib import Path

from jubi.integrations.gemini.llm_client import LLM_Client


SERVER_UNREACHABLE = "[ERROR] Could not connect to the server. Please try again later."


def _error_message(res: Response) -> str:
    """Pull a readable error out of a failed API response."""
    try:
        body = res.json()
    except ValueError:
        return res.text or res.reason
    if isinstance(body, dict):
        return str(body.get("message") or body.get("detail") or res.reason)
    return res.reason


@click.command(name="add", help="Add a new job to be tracked by Jubi")
@click.argument("name", required=False)
@click.argument("company", required=False)
@click.option(
    "--date",
    "-d",
    prompt="Enter the date applied. Default:",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
)
@click.option(
    "--status",
    "-s",
    prompt="Enter the application status. Default:",
    default=f"{JobStatus.APPLIED}",
)
def add(name, company, date, status):
    if name is None:
        name = click.prompt("Enter the job title")
    if company is None:
        company = click.prompt("Enter the company name")

    try:
        res = controller.postJob(name, company, date, status)
    except JobValidationError as e:
        raise click.ClickException(f"[ERROR] Invalid job data: {e}")
    except ConnectionError:
        raise click.ClickException(SERVER_UNREACHABLE)

    if not res.ok:
        raise click.ClickException(f"[ERROR] {_error_message(res)}")

    click.echo(f"{name} at {company} was added to Jubi.")
    if not res.json().get("notification_sent"):
        click.echo("[WARNING] The Discord notification could not be sent.")


@click.command(name="list", help="List all jobs currently being tracked")
@click.option(
    "--status",
    "-s",
    type=click.Choice(
        ["rejected", "applied", "interview", "ghosted", "withdrawn", "oa", "offer"],
        case_sensitive=False,
    ),
    multiple=True,
    help="Filter by Status",
)
def list_jobs(status: tuple):
    try:
        res = controller.getJobs()
    except ConnectionError:
        raise click.ClickException(SERVER_UNREACHABLE)

    if not res.ok:
        raise click.ClickException(f"[ERROR] {_error_message(res)}")

    # GET /jobs/ has no status filter, so filtering happens client-side
    wanted = {"online assessment" if s == "oa" else s for s in status}
    jobs = [(job_id, Job.model_validate(data)) for job_id, data in res.json()]
    jobs = [(job_id, job) for job_id, job in jobs if not wanted or job.status in wanted]

    if not jobs:
        click.echo("No applications found")
        return

    click.echo("----Applications-----")
    for job_id, job in jobs:
        click.echo(
            f"({job_id}) {job.name} at {job.company}. "
            f"Applied on: {job.date_applied.date()} Status: {job.status}."
        )


@click.command(name="history", help="Retrieves the status history of a job")
@click.argument("job_id", type=int)
def history(job_id):
    try:
        res = controller.getStatusHistory(job_id)
    except ConnectionError:
        raise click.ClickException(SERVER_UNREACHABLE)

    if res.status_code == 404:
        raise click.ClickException(f"Job #{job_id} was not found in the tracker")
    elif not res.ok:
        raise click.ClickException(f"[ERROR] {_error_message(res)}")

    status_history = res.json()
    job_name = status_history["job_name"]
    company = status_history["company"]
    changes = status_history["history"]

    click.echo(f"--- Status history for {job_name} at {company} ---")
    for change in changes:
        if change["prev"] == "":
            click.echo(f"[{change['date_change']}] Applied")
        else:
            click.echo(f"[{change['date_change']}] {change['prev']} => {change['new']}")


@click.command(name="delete", help="Remove a job")
@click.argument("job_id", type=int)
def delete(job_id):
    click.confirm("Are you sure you want to delete this job?", abort=True)
    try:
        res = controller.deleteJob(job_id)
    except ConnectionError:
        raise click.ClickException(SERVER_UNREACHABLE)

    if res.status_code == 404:
        click.echo(f"Job #{job_id} was not found in the tracker")
    elif not res.ok:
        raise click.ClickException(
            f"[ERROR] Could not delete Job #{job_id}: {_error_message(res)}"
        )
    else:
        click.echo(f"Job #{job_id} was successfully deleted!")


@click.command(name="update", help="Update job status")
@click.argument("job_id", type=int)
@click.option("--status", "-s", required=True, help="The new status of the application")
def update(job_id, status):
    try:
        res = controller.updateJob(job_id, status)
    except ConnectionError:
        raise click.ClickException(SERVER_UNREACHABLE)

    if res.status_code == 404:
        click.echo(f"Job #{job_id} was not found in the tracker")
    elif res.status_code == 400:
        raise click.ClickException(f"[ERROR] '{status}' is not a valid status")
    elif not res.ok:
        raise click.ClickException(
            f"[ERROR] Could not update Job #{job_id}: {_error_message(res)}"
        )
    else:
        click.echo(f"Job #{job_id}'s status was successfully updated to {status}")


# TODO Handle 400 and Crash
@click.command(name="analyze", help="Analyze your resume against a job description")
@click.argument(
    "job_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
def analyze(job_file):
    click.echo("Your analysis will be sent to Discord. This may take a few minutes...")
    try:
        res = controller.getAnalysis(job_file)
        click.echo("Your resume analysis has just been sent to Discord")
    except ConnectionError:
        raise click.ClickException(SERVER_UNREACHABLE)
    


@click.command(name="upload", help="Upload a resume to Jubi")
@click.argument(
    "resume_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
def upload(resume_file):
    try:
        res = controller.uploadResume(resume_file)
    except ConnectionError:
        raise click.ClickException(SERVER_UNREACHABLE)

    if not res.ok:
        raise click.ClickException(f"[ERROR] {_error_message(res)}")
    else:
        click.echo("Your resume was successfully uploaded to Jubi")


@click.command(name="resumes", help="List resumes")
def resumes():
    try:
        res = controller.getResumes()
    except ConnectionError:
        raise click.ClickException(SERVER_UNREACHABLE)

    if res.status_code == 404:
        raise click.ClickException("No resumes were found")

    if not res.ok:
        raise click.ClickException(f"[ERROR] {_error_message(res)}")

    else:
        list_resumes = res.json()["resumes"]
        for i, resume in enumerate(list_resumes, start=1):
            click.echo(f"({i}) {resume}")
