import sqlite3
from sqlite3 import Connection

from pathlib import Path 
DATABASE_PATH = Path(__file__).resolve().parent / "jubi.db"

def get_database(in_memory: bool) -> Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_PATH) if not in_memory else sqlite3.connect(":memory:")


def init_database(conn: Connection | None = None):
    db_conn = None
    if(conn == None):
        db_conn = get_database(False)
    else:
        db_conn = conn
    try:
        create_db = '''
            CREATE TABLE IF NOT EXISTS jobs(job_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            job_name TEXT NOT NULL, company TEXT NOT NULL, 
            date_applied TEXT NOT NULL, status TEXT NOT NULL)
            '''
        
        db_conn.cursor().execute(create_db)
        db_conn.commit()

    except sqlite3.Error:
        db_conn.rollback()
        raise sqlite3.Error






