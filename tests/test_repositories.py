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
        dir = Path(tmp_path / "fake_desktop")
        dir.mkdir(parents=True, exist_ok=True)
        create_fake_resume(str(dir / "fake_resume.pdf"))

        repo = ResumeRepository(tmp_path / "resumes")

        repo.add_resume(dir / "fake_resume.pdf")

        assert Path(repo.resume_path / "fake_resume.pdf").exists()

    def test_add_resume_doesnt_exist(self, tmp_path):
        # arrange
        dir = Path(tmp_path / "fake_desktop")
        dir.mkdir(parents=True, exist_ok=True)
        create_fake_resume(str(dir / "fake_resume.pdf"))

        repo = ResumeRepository(tmp_path / "resumes")
        bad_resume = Path(tmp_path / "John_Amrous_Resume.pdf")

        with pytest.raises(OSError):
            repo.add_resume(bad_resume)

    def test_get_resumes(self, tmp_path):
        dir = Path(tmp_path / "fake_desktop")
        dir.mkdir(parents=True, exist_ok=True)
        create_fake_resume(str(dir / "fake_resume.pdf"))

        repo = ResumeRepository(tmp_path / "resumes")

        repo.add_resume(dir / "fake_resume.pdf")

        assert len(repo.get_resumes()) == 1
