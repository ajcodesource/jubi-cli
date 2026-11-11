import os
import psycopg as postgres
import pytest
from jubi.core.models.Job import Job, JobStatus


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
