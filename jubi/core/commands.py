import sys
import click
import sqlite3
from pydantic import ValidationError
from jubi.core.models.Job import Job, JobStatus
from datetime import datetime
import requests as r
import json as json


@click.command(name="add", help="Add a new job to be tracked by Jubi")
@click.argument('name')
@click.argument('company')
@click.option("--date", "-d", default=f"{datetime.now().strftime('%Y-%m-%d')}")
@click.option("--status", "-s", default=f"{JobStatus.APPLIED}")
def add(name, company, date, status):
    try:
        job = Job(name=name, company=company, date_applied=date, status=status)
        conn = sqlite3.connect("jubi/core/db/jubi.db")
        conn.cursor().execute(f"INSERT INTO jobs (job_name, company, date_applied, status) VALUES ('{job.name}', '{job.company}', '{job.date_applied}', '{job.status}')")
        conn.commit()
        with open("config.json", "r") as f:
            config = json.load(f)

        webhook = config["webhook"]["url"]
        payload = {
            'content': f'A new job was added to Jubi! It\'s {job.name} @ {job.company}. Good Luck, Akli!',

        }
        ret = r.post(webhook, json=payload)
        click.echo("A job has been added to Jubi. A confirmation message has been sent to Discord!")


    except ValidationError as e:
        click.echo("[ERROR] Arguments invalid")
        click.echo(e)
        sys.exit(1)

@click.command(name="listall", help="List all jobs currently being tracked")
def listall():
    conn = sqlite3.connect("jubi/core/db/jubi.db")
    cursor = conn.cursor()
    cursor.execute("SELECT job_id, job_name, company, date_applied, status from jobs")
    conn.commit()
    result = cursor.fetchall()

    if len(result) == 0:
        click.echo("No applications found")
    else:
        click.echo("----Applications-----")
        for row in result:
            click.echo(f'({row[0]}) {row[1]} at {row[2]}. Applied on: {row[3]} Status: {row[4]}.')

@click.command(name="delete", help="Remove a job from Jubi using a Job ID")
@click.argument('job_id')
def delete(job_id):
    check_if = f"SELECT * FROM jobs WHERE job_id = {job_id}"
    conn = sqlite3.connect("jubi/core/db/jubi.db")
    cursor = conn.cursor()
    cursor.execute(check_if)
    conn.commit()
    if not cursor.fetchall():
        click.echo("No applications found")
    else:
        cursor.execute(f"DELETE FROM jobs WHERE job_id = {job_id}")
        conn.commit()
        click.echo(f"Job #{job_id} deleted")



@click.command(name="alert", help="Discord Test Command")
@click.option("--message", prompt=True, help="Message to send to Discord")
def alert(message:str) -> None:
    with open("config.json", "r") as f:
        config = json.load(f)


    webhook = config["webhook"]["url"]
    payload = {
        'content': f'{message}',

    }
    r.post(webhook, json=payload)
    click.echo("Message sent to Discord")

@click.command(name="init", help="Initialize the application")
def init():
    create_db = '''
    CREATE TABLE IF NOT EXISTS jobs(job_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    job_name TEXT NOT NULL, company TEXT NOT NULL, 
    date_applied TEXT NOT NULL, status TEXT NOT NULL)
    '''
    db_conn = sqlite3.connect("jubi/core/db/jubi.db")
    db_conn.cursor().execute(create_db)
    db_conn.commit()
    click.echo("Database Created!")


@click.command(name="update", help="Update job status")
@click.argument('job_id')
@click.option("--passed", "-p", is_flag=True, default=False)
def update(job_id, passed:bool) -> None:
    check_if = f"SELECT * FROM jobs WHERE job_id = {job_id}"
    conn = sqlite3.connect("jubi/core/db/jubi.db")
    cursor = conn.cursor()
    cursor.execute(check_if)
    conn.commit()
    if not cursor.fetchall():
        click.echo("Application was not found")
        sys.exit(1)
    else:
        update_cmd = f"UPDATE jobs SET status = '{JobStatus.REJECTED if not passed else JobStatus.INTERVIEW }' WHERE job_id = {job_id} "
        cursor.execute(update_cmd)
        conn.commit()
        click.echo("Application updated")




