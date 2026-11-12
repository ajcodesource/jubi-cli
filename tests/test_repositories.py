from pathlib import Path

import psycopg
import pytest

from jubi.core.repository.database import DatabaseController
from jubi.core.repository.resume_repository import ResumeRepository
from psycopg import conninfo
import os


@pytest.fixture(autouse=True)
def use_database(monkeypatch):
    connection_string = os.getenv("TESTDATABASE")
    assert connection_string is not None, (
        "There doesn't seem to be a test database in your .env"
    )

    db_name = conninfo.conninfo_to_dict(connection_string).get("dbname", "")
    assert isinstance(db_name, str) and "test" in db_name
    monkeypatch.setenv("DATABASE", connection_string)
    return connection_string


class TestDatabase:
    def test_dotenv(self):
        assert DatabaseController._get_env_path() == Path(
            "/Users/akliamrous/Documents/Software Projects/Jubi/.env"
        )

    def test_database_creation(self, use_database):
        db_connection = psycopg.connect(use_database)
        DatabaseController.admin_create_tables(db_connection)

        result = db_connection.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = 'jobs'
        """).fetchone()

        result2 = db_connection.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'status_history'
                """).fetchone()

        assert result is not None and result2 is not None


class TestResumeRepository:
    def test_add_resume(self, tmp_path):
        # arrange
        resume = Path("/Users/akliamrous/Desktop/Akli_Amrous_Resume.pdf")
        repo = ResumeRepository(tmp_path / "jubi")

        repo.add_resume(resume)

        assert Path(repo.resume_path / "Akli_Amrous_Resume.pdf").exists()

    def test_add_resume_doesnt_exist(self, tmp_path):
        # arrange
        resume = Path("/Users/akliamrous/Desktop/John_Amrous_Resume.pdf")
        repo = ResumeRepository(tmp_path / "jubi")

        result = repo.add_resume(resume)

        assert result == False

    def test_get_resumes(self, tmp_path):
        resume = Path("/Users/akliamrous/Downloads/Akli_Amrous_Resume.pdf")
        repo = ResumeRepository(tmp_path / "jubi")

        repo.add_resume(resume)

        assert len(repo.get_resumes()) > 0
