from datetime import date
import os
from unittest.mock import MagicMock
from pathlib import Path
import psycopg
import pytest
from psycopg import conninfo
from jubi.core.repository.database import DatabaseController
from jubi.core.repository.resume_repository import ResumeRepository
from jubi.core.services import job_service, resume_service
from jubi.exceptions.exceptions import JobRetrievalError, JobUpdateError, JobValidationError, ResumeUploadError
from jubi.integrations.notifications import Notifications

class TestAddJob:
    def test_add_bad_job(self):
        with pytest.raises(JobValidationError):
            job_service.add_job("Software Engineer", "Meta", date(2026, 11, 11), "labubu")
            job_service.add_job("Software Engineer", "Meta", "cool date", "labubu")
        

class TestListAllJobs:

    def test_list_jobs(self):
        # call job_service.get_all_jobs and get the rows returned
        # There should only be one job
        job_service.add_job("Software Engineer", "Meta", date(2026, 11, 11), "applied")
        rows = job_service.get_all_jobs([])
        assert len(rows) == 1
        assert [[row[1], row[2], row[3], row[4]] for row in rows] == [
            ["Software Engineer", "Meta", date(2026, 11, 11), "applied"]
        ]

    def test_list_jobs_with_status(self):
        # call job_service.get_all_jobs with bad status
        # check if only one job
        job_service.add_job("Software Engineer", "Meta", date(2026, 11, 11), "applied")
        rows = job_service.get_all_jobs(["oa"])
        assert len(rows) == 0

    def test_list_jobs_with_bad_status_input(self):
        job_service.add_job("Software Engineer", "Meta", date(2026, 11, 11), "applied")
        assert job_service.get_all_jobs(["online aessment"]) == []

    def test_list_jobs_returns_nothing(self):
        assert job_service.get_all_jobs(["Cool", "beans"]) == []
            


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
        mock_update = MagicMock(side_effect=JobUpdateError("connection lost"))
        monkeypatch.setattr(
            job_service.job_repository, "update_job_status", mock_update
        )

        with pytest.raises(JobUpdateError):
            job_service.update_status(1, "interview")

    def test_update_status_returns_1_row(self):
        # arrange
        job_service.add_job("Software Engineer", "Meta", date(2026, 11, 11), "applied")
        res = job_service.update_status(1, "interview")
        assert res == 1

    def test_update_status_fail_update(self):
        job_service.add_job("Software Engineer", "Meta", date(2026, 11, 11), "applied")
        with pytest.raises(JobValidationError):
            job_service.update_status(1, "banana")


class TestDelete:
    @pytest.mark.parametrize("repo_result", [True, False])
    def test_delete_job_returns_repo_result(self, monkeypatch, repo_result):
        mock_delete = MagicMock()
        mock_delete.return_value = repo_result

        monkeypatch.setattr(job_service.job_repository, "delete_job", mock_delete)

        assert job_service.delete_job_from_db(1) is repo_result
        mock_delete.assert_called_once_with(1)


class TestNotifications:
    def test_notification_fail(self, monkeypatch):
        monkeypatch.delenv("WEBHOOK")

        with pytest.raises(RuntimeError):
            Notifications()

class TestResumeService:
    def test_add_resume(self, tmp_path):
        # add the resume
        resume = Path("/Users/akliamrous/Desktop/Akli_Amrous_Resume_Data.pdf")
        result = resume_service.upload_resume(resume, tmp_path / "jubi")

        assert result == True 

        # get resumes
        resume_list = resume_service.get_resumes(tmp_path / "jubi")
        assert len(resume_list) == 1
        assert "Akli_Amrous_Resume_Data.pdf" in str(resume_list[0])
        assert Path(tmp_path / "jubi" / "Akli_Amrous_Resume_Data.pdf") == resume_list[0]

    def test_add_resume_does_not_exist(self, tmp_path):
        # add the resume
        resume = Path("/Users/akliamrous/Desktop/Akli_Amrous_Data.pdf")
        result = resume_service.upload_resume(resume, tmp_path / "jubi")

        assert result == False

        # get resumes
        resume_list = resume_service.get_resumes(tmp_path / "jubi")
        assert len(resume_list) == 0
        assert Path(tmp_path / "jubi" / "Akli_Amrous_Data.pdf") not in resume_list


    def test_add_resume_os_error(self, tmp_path, monkeypatch):
        def mock_add_resume(*args, **kwargs):
            raise OSError("Something went wrong with the file system")

        monkeypatch.setattr(ResumeRepository, "add_resume", mock_add_resume)

        with pytest.raises(ResumeUploadError):
            resume = Path("/Users/akliamrous/Desktop/Akli_Amrous_Resume_Data.pdf")
            result = resume_service.upload_resume(resume, tmp_path / "jubi")
            
