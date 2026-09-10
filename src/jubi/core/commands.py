import sys
import click
import sqlite3
from pydantic import ValidationError
from jubi.core.models.Job import Job, JobStatus
from jubi.core.models.Event import Event, EventType
from jubi.utils.notifications import Notifications
from jubi.core.db.jobs import add_job, list_all_jobs, delete_job, update_job_status, filter_status
from jubi.core.db.database import init_database
from datetime import datetime
import requests as r
import json as json


@click.command(name="add", help="Add a new job to be tracked by Jubi")
@click.argument('name')
@click.argument('company') 
@click.option("--date", "-d", type=click.DateTime(formats=["%Y-%m-%d"]), default=f"{datetime.now().strftime('%Y-%m-%d')}")
@click.option("--status", "-s", default=f"{JobStatus.APPLIED}")
def add(name, company, date, status):
    try:
        if(not Job.convert(status)):
            click.echo("ERROR: Invalid Status")
        else:
            status_app = Job.convert(status) 
            status_to_apply = status_app if status_app else JobStatus.APPLIED
            validate = Job(name=name, company=company, date_applied=date, status= status_to_apply)
            add_job(validate.name, validate.company, validate.date_applied, validate.status)
    except ValidationError as e:
        click.echo("[ERROR] Arguments invalid. --help")
        click.echo(e)
        sys.exit(1)

@click.command(name="listall", help="List all jobs currently being tracked")
def listall():

    all_jobs = list_all_jobs()

    if not all_jobs:
        click.echo("No applications found")
    else:
        click.echo("----Applications-----")
        for row in all_jobs:
            click.echo(f'({row[0]}) {row[1]} at {row[2]}. Applied on: {row[3]} Status: {row[4]}.')

@click.command(name="delete", help="Remove a job from Jubi using a Job ID")
@click.argument('job_id')
def delete(job_id):
    delete_job(job_id)


@click.command(name="init", help="Initialize the application")
def init():
    init_database()


@click.command(name="status", help="Display application status list")
@click.option("--rejection", "-r", is_flag=True, default=False)
@click.option("--applied", "-a", is_flag=True, default=False)
@click.option("--interview", "-i", is_flag=True, default=False)
@click.option("--offer", "-o", is_flag=True, default=False)
def status(rejection:bool, applied:bool, interview:bool, offer:bool):
    filter_status(rejection, applied, interview, offer)

    
@click.command(name="update", help="Update job status")
@click.argument('job_id')
@click.option("--status", "-s", help="The new status of the application")
def update(job_id, status):
    update_job_status(job_id, status)
