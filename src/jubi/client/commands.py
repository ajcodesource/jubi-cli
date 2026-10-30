import click
import psycopg as postgres
from jubi.core.models.Job import JobStatus
from jubi.core.services import job_service, resume_service
from jubi.utils.exceptions import (
    JobDescriptionError,
    JobWriteError,
    JobValidationError,
    NotificationError,
    ResumeAccessError,
    ResumeUploadError,
)
from jubi.core.repository.database import DatabaseController as db
from datetime import datetime
import json as json
from pathlib import Path


@click.command(name="add", help="Add a new job to be tracked by Jubi")
@click.argument("name", required=False)
@click.argument("company", required=False)
@click.option(
    "--date",
    "-d",
    prompt="Enter the date applied. Default:",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    default=f"{datetime.now().strftime('%Y-%m-%d')}",
)
@click.option(
    "--status",
    "-s",
    prompt="Enter the application status. Default:",
    default=f"{JobStatus.APPLIED}",
)
@click.option("--url", "-u", help="Greenhouse or Lever URL")
def add(name, company, date, status, url):
    try:
        if name is None:
            name = click.prompt("Enter the job title")
        if company is None:
            company = click.prompt("Enter the company name")
        job_service.add_job(name, company, date, status)
        click.echo(f"The job {name} at {company} was successfully added")
        click.echo("An alert has just been sent to Discord")
    except JobValidationError as e:
        raise click.ClickException(f"[ERROR] Invalid job data: {e}")
    except JobWriteError as e:
        raise click.ClickException(f"[ERROR] {e}")
    except NotificationError as e:
        raise click.ClickException(
            "[ERROR] Failed to send notification but job added successfully"
        )


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
def list_jobs(status):
    try:
        all_jobs = job_service.get_all_jobs(
            "online assessment" if s == "oa" else s for s in list(status)
        )
        # click.echo(all_jobs)

        if not all_jobs:
            click.echo("No applications found")
        else:
            click.echo("----Applications-----")
            for row in all_jobs:
                click.echo(
                    f"({row[0]}) {row[1]} at {row[2]}. Applied on: {row[3]} Status: {row[4]}."
                )
    except postgres.Error as e:
        raise click.ClickException(f"Error: A Database Error Occurred {e}")


@click.command(name="delete", help="Remove a job from Jubi using a Job ID")
@click.argument("job_id")
def delete(job_id):
    if click.confirm("Are you sure you want to delete this job?", abort=True):
        try:
            success = job_service.delete_job_from_db(job_id)
            if success:
                click.echo(f"Job #{job_id} was successfully deleted!")
            else:
                click.echo(f"Job #{job_id} was not found in the tracker")
        except postgres.Error as e:
            raise click.ClickException(f"Error{e}")


@click.command(name="update", help="Update job status")
@click.argument("job_id")
@click.option("--status", "-s", help="The new status of the application")
def update(job_id, status):
    try:
        success = job_service.update_status(job_id, status)
        if success:
            click.echo(f"Job #{job_id}'s status was successfully updated to {status}")
        else:
            click.echo(f"Job #{job_id} was not found in the tracker")
    except postgres.Error as e:
        raise click.ClickException(f"Error {e}")


@click.command(name="analyze", help="Analyze your resume against a job description")
@click.argument(
    "job_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
def analyze(job_file):
    click.echo("Your analysis will be sent to Discord. This may take a few minutes...")
    try:
        resume_service.analyze_resume(job_file)
        click.echo("Your resume analysis has just been sent to Discord")
    except (ResumeAccessError, ResumeUploadError, JobDescriptionError) as e:
        raise click.ClickException(f"[ERROR] {e}")
    except NotificationError as e:
        raise click.ClickException(
            f"[ERROR] Analysis finished but failed to send to Discord: {e}"
        )


@click.command(name="upload", help="Upload a resume to Jubi")
@click.argument(
    "resume_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
def upload(resume_file):
    try:
        resume_service.upload_resume(resume_file)
        click.echo("Upload successful")
    except (ResumeAccessError, ResumeUploadError, JobDescriptionError) as e:
        raise click.ClickException(f"[ERROR] {e}")
