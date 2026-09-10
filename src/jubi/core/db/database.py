import sqlite3
import os
from pathlib import Path 
import click

DATABASE_PATH = Path(__file__).resolve().parent / "jubi.db"

def get_database():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DATABASE_PATH)


def init_database():
    db_conn = get_database()
    try:
        create_db = '''
            CREATE TABLE IF NOT EXISTS jobs(job_id INTEGER PRIMARY KEY AUTOINCREMENT, 
            job_name TEXT NOT NULL, company TEXT NOT NULL, 
            date_applied TEXT NOT NULL, status TEXT NOT NULL)
            '''
        
        db_conn.cursor().execute(create_db)
        click.echo("Database Created!")
        db_conn.commit()
    except sqlite3.Error:
        db_conn.rollback()
        
    finally:
        db_conn.close()


