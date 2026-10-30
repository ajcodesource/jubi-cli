import os
from pathlib import Path
from click.testing import CliRunner
import pytest
from requests import RequestException
import psycopg as postgres
from unittest.mock import MagicMock
import platformdirs
from jubi.core.models.Job import Job, JobStatus
from jubi.core.repository import job_repository
from jubi.core.services import job_service
from jubi.core.repository.database import DatabaseController
from jubi.utils.notifications import Notifications
from jubi.core.repository.resume_repository import ResumeRepository


@pytest.fixture
def db_connection():
    conn = postgres.connect(os.environ["TESTDATABASE"])
    try:
        yield conn

    finally:
        conn.rollback()
        conn.close()


class TestModel:
    @pytest.mark.parametrize(
        "test_string,expected",
        [
            ("applied", JobStatus.APPLIED),
            ("rejected", JobStatus.REJECTED),
            ("interview", JobStatus.INTERVIEW),
            ("offer", JobStatus.OFFER),
            ("ghosted", JobStatus.GHOSTED),
            ("withdrawn", JobStatus.WITHDRAWN),
            ("online assessment", JobStatus.OA),
        ],
    )
    def test_model_conversion(self, test_string, expected):
        assert Job.convert(test_string) == expected

    @pytest.mark.parametrize(
        "test_string,expected",
        [
            ("aplied", None),
            ("failed", None),
            ("started", None),
        ],
    )
    def test_model_conversion_fail(self, test_string, expected):

        assert Job.convert(test_string) == expected


class TestUpdateStatus:
    @pytest.mark.parametrize("repo_result", [True, False])
    def test_update_status_returns_repository_result(self, monkeypatch, repo_result):
        mock_update = MagicMock(return_value=repo_result)
        monkeypatch.setattr(
            job_service.job_repository, "update_job_status", mock_update
        )

        assert job_service.update_status(1, "interview") is repo_result
        mock_update.assert_called_once_with(job_id=1, new_status="interview")

    def test_update_status_propagates_db_error(self, monkeypatch):
        mock_update = MagicMock(side_effect=postgres.Error("connection lost"))
        monkeypatch.setattr(
            job_service.job_repository, "update_job_status", mock_update
        )

        with pytest.raises(postgres.Error):
            job_service.update_status(1, "interview")


class TestDelete:
    @pytest.mark.parametrize("repo_result", [True, False])
    def test_delete_job_returns_repo_result(self, monkeypatch, repo_result):
        mock_delete = MagicMock()
        mock_delete.return_value = repo_result

        monkeypatch.setattr(job_service.job_repository, "delete_job", mock_delete)

        assert job_service.delete_job_from_db(1) is repo_result
        mock_delete.assert_called_once_with(1)


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


class TestNotifications:
    def test_notification_fail(self, monkeypatch):
        monkeypatch.delenv("WEBHOOK")

        with pytest.raises(RuntimeError):
            notification_class = Notifications()


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
