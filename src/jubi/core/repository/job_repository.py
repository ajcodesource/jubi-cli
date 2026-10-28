from pathlib import Path

from jubi.core.repository.database import DatabaseController as db
from datetime import datetime
from dotenv import load_dotenv
import os


def add_job(name, company, date_applied, status) -> bool:
    conn = db.get_PG_database()
    db.init_pg_database(conn)

    new_conn = db.get_PG_database()
    with new_conn as pg_conn:
        with pg_conn.cursor() as cur:
            cur.execute(
                """
                    INSERT INTO jobs
                        (name, company, date_applied, status)
                    VALUES (%s, %s, %s, %s)
                    RETURNING job_id
                    """,
                (name, company, date_applied, status),
            )
            row = cur.fetchone()
            assert row is not None  # RETURNING always gives back the inserted row
            job_id = row[0]
            cur.execute(
                """
                        INSERT INTO status_history(job_id, prev_status, new_status, date_change )
                        VALUES (%s, %s, %s, %s)

                    """,
                (job_id, "", status, datetime.now()),
            )
    return True


# "DELETE FROM jobs WHERE job_id = ?", (job_id,)
# "SELECT * FROM jobs WHERE job_id = ?", (job_id,)


def list_all_jobs(filters: list[str]):
    conn = db.get_PG_database()
    db.init_pg_database(conn)
    new_conn = db.get_PG_database()
    with new_conn as pg_conn:
        with pg_conn.cursor() as cursor:
            if not filters:
                cursor.execute(
                    "SELECT job_id, name, company, date_applied, status FROM jobs"
                )
            else:
                cursor.execute(
                    """
                    SELECT job_id, name, company, date_applied, status
                    FROM jobs
                    WHERE status = ANY(%s)
                    """,
                    (list(filters),),
                )
            return cursor.fetchall()


def delete_job(job_id):
    conn = db.get_PG_database()
    db.init_pg_database(conn)
    new_conn = db.get_PG_database()
    with new_conn as pg_conn:
        with pg_conn.cursor() as cursor:
            select = cursor.execute(
                """
                SELECT * FROM jobs WHERE job_id = %s
            
            """,
                (job_id,),
            )
            check = select.fetchall()
            if check == []:
                return False
            else:
                # status_history rows reference this job, so they have to go first
                cursor.execute(
                    """
                DELETE FROM status_history WHERE job_id = %s
                """,
                    (job_id,),
                )
                cursor.execute(
                    """
                DELETE FROM jobs WHERE job_id = %s
            
            """,
                    (job_id,),
                )
    return True


# cursor.execute("UPDATE jobs SET status = ? WHERE job_id = ?", (new_status, job_id,))
def update_job_status(job_id: int, new_status: str) -> bool:
    conn = db.get_PG_database()
    db.init_pg_database(conn)
    new_conn = db.get_PG_database()
    with new_conn as pg_conn:
        with pg_conn.cursor() as cursor:
            ex = cursor.execute(
                """
                SELECT * FROM jobs WHERE job_id = %s
                        
                    """,
                (job_id,),
            )
            jobs = cursor.fetchall()
            if jobs == []:
                return False
            else:
                cursor.execute(
                    """  
                    INSERT INTO status_history(job_id, prev_status, new_status, date_change )
                    VALUES (%s, %s, %s, %s)

                """,
                    (job_id, jobs[0][4], new_status, datetime.now()),
                )
                cursor.execute(
                    """UPDATE jobs SET status = %s WHERE job_id = %s""",
                    (
                        new_status,
                        job_id,
                    ),
                )
                return True
