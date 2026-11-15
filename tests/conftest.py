import os
from pathlib import Path
from dotenv import load_dotenv
from psycopg import conninfo
import psycopg
import pytest
from jubi.core.repository.database import DatabaseController
from google.genai import errors

dotenv_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=dotenv_path)


@pytest.fixture(autouse=True)
def get_database(monkeypatch):
    connection_string = os.getenv("TESTDATABASE")
    assert connection_string is not None, "No connection string in env"
    db = conninfo.conninfo_to_dict(connection_string).get("dbname", "")
    assert isinstance(db, str) and "test" in db, (
        "Connection String doesnt seem to be a test database"
    )
    monkeypatch.setenv("DATABASE", connection_string)
    connection = psycopg.connect(connection_string)
    connection.execute("DROP TABLE IF EXISTS status_history, jobs")
    DatabaseController.init_pg_database(connection)
    return connection_string


@pytest.fixture
def fake_llm_client_client_error():
    class Fake_LLM_Client:
        def __init__(self):
            pass

        def send_prompt(*args, **kwargs):
            raise errors.ClientError(400, "Client Error")

    llm_client = Fake_LLM_Client()
    return llm_client


@pytest.fixture
def fake_llm_client_api_error():
    class Fake_LLM_Client:
        def __init__(self):
            pass

        def send_prompt(*args, **kwargs):
            raise errors.APIError(500, "API Error")

    llm_client = Fake_LLM_Client()
    return llm_client
