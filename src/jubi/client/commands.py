import sys
import click
import sqlite3
from pydantic import ValidationError
from jubi.core.models.Job import Job, JobStatus
from jubi.core.services import job_controller
from jubi.utils.exceptions import JobWriteError, JobValidationError, NotificationError
from jubi.utils.notifications import Notifications
from jubi.core.repository.database import init_database
from datetime import datetime
import requests as r
import json as json
from pathlib import Path

@click.command(name="add", help="Add a new job to be tracked by Jubi")
@click.argument('name')
@click.argument('company') 
@click.option("--date", "-d", type=click.DateTime(formats=["%Y-%m-%d"]), default=f"{datetime.now().strftime('%Y-%m-%d')}")
@click.option("--status", "-s", default=f"{JobStatus.APPLIED}")
def add(name, company, date, status):
    path = Path(__file__).resolve().parent.parent / "core/repository/jubi.db"
    
    if(not path.exists()):
        raise click.ClickException("[ERROR] The database has not been initialized. Run 'jubi init' to initialize")

    try:
        job_controller.add_job(name, company, date, status)
    except JobValidationError as e:
        raise click.ClickException(f"[ERROR] Invalid job data: {e}")
    except JobWriteError as e:
        raise click.ClickException(f"[ERROR] {e}")
    except NotificationError as e:
        raise click.ClickException("[ERROR] Failed to send notification but job added successfully")
    

@click.command(name="list", help="List all jobs currently being tracked")
@click.option("--rejection", "-r", is_flag=True, default=False)
@click.option("--applied", "-a", is_flag=True, default=False)
@click.option("--interview", "-i", is_flag=True, default=False)
@click.option("--offer", "-o", is_flag=True, default=False)
def list_jobs(rejection, applied, interview, offer):
    path = Path(__file__).resolve().parent.parent / "core/repository/jubi.db"
    if(not path.exists()):
        raise click.ClickException("[ERROR] The database has not been initialized. Run 'jubi init' to initialize")
   
    try:
        all_jobs = job_controller.get_all_jobs(rejection, applied, interview, offer)

        if not all_jobs:
            click.echo("No applications found")
        else:
            click.echo("----Applications-----")
            for row in all_jobs:
                click.echo(f'({row[0]}) {row[1]} at {row[2]}. Applied on: {row[3]} Status: {row[4]}.')
    except sqlite3.Error as e:
        raise click.ClickException(f"Error: A Database Error Occurred {e}")


@click.command(name="delete", help="Remove a job from Jubi using a Job ID")
@click.argument('job_id')
def delete(job_id):
    path = Path(__file__).resolve().parent.parent / "core/repository/jubi.db"
    if(not path.exists()):
        raise click.ClickException("[ERROR] The database has not been initialized. Run 'jubi init' to initialize")
    if(click.confirm("Are you sure you want to delete this job?", abort=True)):
        try:
            success = job_controller.delete_job_from_db(job_id)
            if(success):
                click.echo(f"Job #{job_id} was successfully deleted!")
            else:
                click.echo(f"Job #{job_id} was not found in the tracker")
        except sqlite3.Error as e:
            raise click.ClickException(f"Error{e}")
        


@click.command(name="init", help="Initialize the application")
def init():  
    init_database()

    
@click.command(name="update", help="Update job status")
@click.argument('job_id')
@click.option("--status", "-s", help="The new status of the application")
def update(job_id, status):
    path = Path(__file__).resolve().parent.parent / "core/repository/jubi.db"
    if(not path.exists()):
        raise click.ClickException("[ERROR] The database has not been initialized. Run 'jubi init' to initialize")
    try:
        success = job_controller.update_status(job_id, status)
        if(success):
            click.echo(f"Job #{job_id}'s status was successfully updated to {status}")
        else:
            click.echo(f"Job #{job_id} was not found in the tracker")
    except sqlite3.Error as e:
        raise click.ClickException(f"Error {e}")
