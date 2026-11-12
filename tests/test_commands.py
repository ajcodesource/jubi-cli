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
from jubi.integrations.notifications import Notifications
from jubi.core.repository.resume_repository import ResumeRepository


# TODO CLI RUNNER
