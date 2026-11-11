from unittest.mock import MagicMock

import psycopg as postgres
import pytest

from jubi.core.services import job_service
from jubi.integrations.notifications import Notifications


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
class TestNotifications:
    def test_notification_fail(self, monkeypatch):
        monkeypatch.delenv("WEBHOOK")

        with pytest.raises(RuntimeError):
            notification_class = Notifications()