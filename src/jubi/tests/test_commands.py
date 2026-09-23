from click.testing import CliRunner
import pytest
from requests import RequestException
from jubi.client.commands import add
from jubi.core.services import job_controller
from jubi.client.commands import list_jobs
from jubi.core.repository.database import init_database, get_database
from jubi.core.repository import database
from jubi.core.repository.job_repository import *
import sqlite3
from unittest.mock import MagicMock
from jubi.utils.exceptions import *
from jubi.core.repository import job_repository


def test_list_jobs(monkeypatch):
    def test_fake_list_jobs(rejection:bool, applied:bool, interview:bool, offer:bool):
        raise sqlite3.Error("DISK I/O Failure")

    monkeypatch.setattr(job_controller, "get_all_jobs", test_fake_list_jobs)

    runner = CliRunner()
    result = runner.invoke(list_jobs, [])
    assert "DISK I/O Failure" in result.output 
    assert result.exit_code == 1

def test_init_successful():
    
    conn = get_database(True)
    init_database(conn)

    cursor = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
    """)

    tables = [row[0] for row in cursor]

    assert "jobs" in tables

    conn.close()

def test_init_fail():
    conn = MagicMock()
    conn.cursor().execute.side_effect = sqlite3.OperationalError("database error")

    with pytest.raises(sqlite3.Error):
        init_database(conn)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()

def test_add_job_fail(monkeypatch):
    conn = MagicMock()
    conn.cursor().execute.side_effect = sqlite3.IntegrityError("Add job fail")

    # add_job() calls db.get_database(False) internally - patch the factory
    # so it hands back our mock connection instead of a real sqlite3 one.
    monkeypatch.setattr(db, "get_database", lambda in_memory: conn)

    with pytest.raises(sqlite3.Error):
        add_job("Engineer", "Acme", "2026-09-21", "applied")

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()
    conn.close.assert_called_once()

def test_add_job_success(monkeypatch):
    conn = MagicMock()

    monkeypatch.setattr(db, "get_database", lambda in_memory: conn)
    add_job("Engineer", "Acme", "2026-09-21", "applied")

    conn.commit.assert_called_once()

def test_list_jobs_fail(monkeypatch):
    conn = MagicMock()
    conn.cursor().execute.side_effect = sqlite3.OperationalError("COuld not get jobs")
    monkeypatch.setattr(db, "get_database", lambda in_memory: conn)

    with pytest.raises(sqlite3.Error):
        list_all_jobs(False, False, False, False)

   
    conn.close.assert_called_once()



def test_list_jobs_db(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")
    conn = get_database(False)
    init_database(conn)
    add_job("Engineer", "Acme", "2026-09-21", "applied")
    result = list_all_jobs(False, False, False, False)

    results = [row for row in result]
    assert results[0] == (1, "Engineer", "Acme", "2026-09-21", "applied")

def test_list_jobs_db_filters(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test2.db")
    conn = get_database(False)
    init_database(conn)
    add_job("Engineer", "Acme", "2026-09-21", "applied")
    result = list_all_jobs(True, False, False, False)

    filtered = [row for row in result]
    assert len(filtered) == 0

def test_delete_jobs_db(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test3.db")

    conn = get_database(False)
    init_database(conn)
    add_job("Software Engineer", "Eggman Empire", "2026-09-21", "offer")

    result = delete_job(1)

    assert result == True

def test_delete_jobs_fail(monkeypatch):
    conn = MagicMock()

    conn.cursor().execute.side_effect = sqlite3.OperationalError("failed to delete")

    monkeypatch.setattr(db, "get_database", lambda in_memory: conn)

    with pytest.raises(sqlite3.Error):
        delete_job(1)

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()


def test_update_job(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test4.db")

    conn = get_database(False)

    init_database(conn)
    add_job("Software Engineer", "Eggman Empire", "2026-09-21", "offer")

    update_job_status(1, "rejected")
    result = list_all_jobs(True, False, False, False)

    assert result[0] == (1, "Software Engineer", "Eggman Empire", "2026-09-21", "rejected")


def test_add_job_fail_convert():
    bad_status = "Tyler"

    with pytest.raises(JobValidationError, match="Status Incorrect"):
        job_controller.add_job("Software Developer", "Westside Fairytales, LLC", "2026-09-21", bad_status)

def test_add_job_fail_validate():
    # status must be valid so we actually reach Job(...) construction instead
    # of failing earlier at Job.convert() (that's test_add_job_fail_convert).
    with pytest.raises(JobValidationError):
        job_controller.add_job("Software Engineer", 2, 3, "applied")

def test_add_job_fail_success_no_notif(monkeypatch):
    def mock_discord_notif(*args, **kwargs):
        raise RequestException("HTTP404: Discord is unavailable")

    # Notifications.__init__ reads the WEBHOOK env var and raises if it's
    # missing, so the class itself needs to be a no-op stand-in here -
    # otherwise this test only passes on machines with a real .env file.
    mock_notifications = MagicMock()
    mock_notifications.return_value.add_notif = mock_discord_notif

    monkeypatch.setattr(job_controller, "Notifications", mock_notifications)
    monkeypatch.setattr(job_repository, "add_job", lambda name, company, date_applied, status: True)

    with pytest.raises(NotificationError):
        job_controller.add_job("Software Engineer", "Westside Fairytales LLC", "2026-09-21", "rejected")


    
    




    











    
    









    
    


