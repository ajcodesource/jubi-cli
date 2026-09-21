from click.testing import CliRunner
import pytest
from jubi.client.commands import add
from jubi.core.services import job_controller
from jubi.client.commands import list_jobs
from jubi.core.repository.database import init_database, get_database
from jubi.core.repository.job_repository import *
import sqlite3
from unittest.mock import MagicMock



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
    









    
    


