from pathlib import Path

import psycopg
import pytest

from jubi.core.repository.database import DatabaseController
from jubi.core.repository.resume_repository import ResumeRepository
from psycopg import conninfo
import os
from fpdf import FPDF

def create_fake_resume(dir):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=16)

    # Add a centered title
    pdf.cell(
        w=0,
        h=10,
        text="Hello, World!",
        new_x="LMARGIN",
        new_y="NEXT",
        align="C",
    )

    # Add body text
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(
        w=0,
        h=8,
        text="This is a test resume. Perform your analysis as if this were a standard software engineering resume",
    )

    # Save the file

    pdf.output(dir)


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
        resume = Path("/Users/akliamrous/Downloads/Resume_Akli_Amrous_Backend-2.pdf")
        repo = ResumeRepository(tmp_path / "jubi")

        repo.add_resume(resume)

        assert Path(repo.resume_path / "Resume_Akli_Amrous_Backend-2.pdf").exists()

    def test_add_resume_doesnt_exist(self, tmp_path):
        # arrange
        resume = Path("/Users/akliamrous/Desktop/John_Amrous_Resume.pdf")
        repo = ResumeRepository(tmp_path / "jubi")
        with pytest.raises(OSError):
            repo.add_resume(resume)

    def test_get_resumes(self, tmp_path):
        resume = Path("/Users/akliamrous/Downloads/Akli_Amrous_Resume.pdf")
        repo = ResumeRepository(tmp_path / "jubi")

        repo.add_resume(resume)

        assert len(repo.get_resumes()) > 0
