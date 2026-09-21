import sqlite3
from jubi.core.repository import database as db 

def add_job(name, company, date_applied, status) -> bool:
    conn = db.get_database(False)
    try:
        conn.cursor().execute("""INSERT INTO jobs 
                            (job_name, company, date_applied, status) 
                            VALUES (?, ?, ?, ?)""", (name, company, date_applied, status,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def list_all_jobs(rejection:bool, applied:bool, interview:bool, offer:bool):
    conn = db.get_database(False)
    filter_rejected = f"{"status = 'rejected'" if rejection else ""}"
    filter_applied = f"{"status = 'applied'" if applied else ""}"
    filter_interview = f"{"status = 'interview'" if interview else ""}"
    filter_offer = f"{"status = 'offer'" if offer else ""}"
    filters = [filter_rejected, filter_applied, filter_interview, filter_offer]
    try:
        cursor = conn.cursor()
        if filters == ["", "", "", ""]:
            cursor.execute("SELECT job_id, job_name, company, date_applied, status from jobs")
            result = cursor.fetchall()
            return result
        else:
            filter_str = ""
            for i in range(len(filters)):
                if(filter_str != "" and filters[i] != ""):
                    filter_str += " OR "
                filter_str += filters[i]
                    
            cursor.execute(f"SELECT * FROM jobs WHERE {filter_str}")
            results = cursor.fetchall()
            return results

    finally:
        conn.close()

def delete_job(job_id):
    conn = db.get_database(False)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        if not cursor.fetchall():
            return False
        else:
            
            cursor.execute("DELETE FROM jobs WHERE job_id = ?", (job_id,))
            conn.commit()
            return True
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def update_job_status(job_id: int, new_status: str) -> bool:
    conn = db.get_database(False)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        ret = cursor.fetchone() 
        if ret is None:
            return False
        else:
            cursor.execute("UPDATE jobs SET status = ? WHERE job_id = ?", (new_status, job_id,))
            conn.commit()
            return True
    except sqlite3.Error as e:
        conn.rollback()
        raise e
    finally:
        conn.close()





    