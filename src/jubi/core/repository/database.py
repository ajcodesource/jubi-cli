from dotenv import load_dotenv
import psycopg as postgres
from psycopg import Connection as PGConnection
import os
from pathlib import Path

dotenv_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=dotenv_path)


class DatabaseController:
    @staticmethod
    def get_PG_database() -> PGConnection:
        return postgres.connect(os.environ["DATABASE"])

    @staticmethod
    def init_pg_database(connect: PGConnection):
        pg_conn = connect
        with pg_conn as conn:
            # 2. Open a cursor to perform database operations
            with conn.cursor() as cur:
                # Create a sample table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS jobs (
                        job_id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        company TEXT NOT NULL, 
                        date_applied DATE NOT NULL, 
                        status TEXT NOT NULL
                    );
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS status_history (
                        transaction_id SERIAL PRIMARY KEY,
                        job_id INT REFERENCES jobs(job_id),
                        prev_status TEXT NOT NULL,
                        new_status TEXT NOT NULL,
                        date_change DATE NOT NULL

                    );
                        """)

    @staticmethod
    def admin_create_tables(connect: PGConnection):
        pg_conn = connect
        cur = pg_conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                company TEXT NOT NULL,
                date_applied DATE NOT NULL,
                status TEXT NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS status_history (
                transaction_id SERIAL PRIMARY KEY,
                job_id INT REFERENCES jobs(job_id),
                prev_status TEXT NOT NULL,
                new_status TEXT NOT NULL,
                date_change DATE NOT NULL
            );
        """)
