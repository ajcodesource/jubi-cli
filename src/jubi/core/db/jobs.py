import sqlite3
from jubi.core.db import database as db 
from jubi.utils.notifications import Notifications
import click
import sys
from jubi.core.models.Job import Job


def add_job(name, company, date_applied, status):
    conn = db.get_database()
    try:
        conn.cursor().execute("""INSERT INTO jobs 
                            (job_name, company, date_applied, status) 
                            VALUES (?, ?, ?, ?)""", (name, company, date_applied, status,))
        conn.commit()
        notif = Notifications()
        notif.add_notif(name, company)
    finally:
        conn.close()

def list_all_jobs():
    conn = db.get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT job_id, job_name, company, date_applied, status from jobs")
        result = cursor.fetchall()
        return result
    except sqlite3.Error:
        conn.rollback()
    finally:
        conn.close()

def delete_job(job_id):
    if(not job_id.isdigit()):
        click.echo("[ERROR] Invalid Job ID")
        sys.exit(1)
    conn = db.get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        conn.commit()
        if not cursor.fetchall():
            click.echo("No applications found")
        else:
            if(click.confirm("Are you sure you want to delete this job?", abort=True)):
                cursor.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
                conn.commit()
                click.echo(f"Job #{job_id} deleted")
    except sqlite3.Error:
        conn.rollback()
    finally:
        conn.close()

def update_job_status(job_id, new_status):
    conn = db.get_database()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        ret = cursor.fetchone() 
        if ret is None:
            click.echo("Application was not found")
            sys.exit(1)
        else:
            job_name, company = ret[1], ret[2]
            cursor.execute("UPDATE jobs SET status = ? WHERE job_id = ?", (new_status, job_id,))
            conn.commit()
            notif = Notifications()
            notif.update_notif(job_name, company)
            click.echo("Application updated")
    except sqlite3.Error:
        conn.rollback()
    finally:
        conn.close()


def filter_status(rejection:bool, applied:bool, interview:bool, offer:bool):
    conn = db.get_database()
    try:
        cursor = conn.cursor()

        filter_rejected = f"{"status = 'rejected'" if rejection else ""}"
        filter_applied = f"{"status = 'applied'" if applied else ""}"
        filter_interview = f"{"status = 'interview'" if interview else ""}"
        filter_offer = f"{"status = 'offer'" if offer else ""}"
        filters = [filter_rejected, filter_applied, filter_interview, filter_offer]
        if filters == ["", "", "", ""]:
            cursor.execute("SELECT job_id, job_name, company, date_applied, status from jobs")
            result = cursor.fetchall()
            for row in result:
                click.echo(f'({row[0]}) {row[1]} at {row[2]}. Applied on: {row[3]} Status: {row[4]}.')
        else:
            filter_str = ""
            for i in range(len(filters)):
                if(filter_str != "" and filters[i] != ""):
                    filter_str += " OR "
                filter_str += filters[i]
                    
            cursor.execute(f"SELECT * FROM jobs WHERE {filter_str}")
            results = cursor.fetchall()
            for res in results:
                click.echo(f"({res[4]}) {res[1]} @ {res[2]}")
    finally:
        conn.close()
    
    