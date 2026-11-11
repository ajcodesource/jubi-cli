
from pathlib import Path

from jubi.core.repository.database import DatabaseController
from jubi.core.repository.resume_repository import ResumeRepository


class TestDatabase:
    def test_database_creation(self, monkeypatch, db_connection):
        monkeypatch.setenv("DATABASE", "TESTDATABASE")

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
    def test_add_resume(self):
        # arrange
        resume = Path("/Users/akliamrous/Desktop/Akli_Amrous_Resume.pdf")
        repo = ResumeRepository()

        repo.add_resume(resume)

        assert Path(repo.resume_path / "Akli_Amrous_Resume.pdf").exists()

    def test_add_resume_doesnt_exist(self):
        # arrange
        resume = Path("/Users/akliamrous/Desktop/John_Amrous_Resume.pdf")
        repo = ResumeRepository()

        result = repo.add_resume(resume)

        assert result == False

    def test_get_resumes(self):
        resume = Path("/Users/akliamrous/Downloads/Akli_Amrous_Resume.pdf")
        repo = ResumeRepository()

        repo.add_resume(resume)

        assert len(repo.get_resumes()) > 0