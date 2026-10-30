import requests as r
import sys
import click
from pathlib import Path
from dotenv import load_dotenv
import os
from jubi.core.models.ResumeAnalysis import ResumeModelResponse

dotenv_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=dotenv_path)


class Notifications:
    def __init__(self):

        config = os.getenv("WEBHOOK")
        if config is None:
            raise RuntimeError(f"WEBHOOK is missing. Expected it in {dotenv_path}")
        self.webhook: str = config

    def update_notif(self, job_name, company):
        payload = {
            "content": f"An update to the position: {job_name} @ {company} was just made.",
        }
        try:
            ret = r.post(self.webhook, json=payload, timeout=10)
        except r.exceptions.RequestException as Error:
            raise Error

    def add_notif(self, job, company):
        payload = {
            "content": f"A new job was added to Jubi! It's {job} @ {company}. Good Luck, Akli!",
        }
        try:
            ret = r.post(self.webhook, json=payload, timeout=10)
        except r.exceptions.RequestException as Error:
            raise Error

    def analysis_notif(self, response: ResumeModelResponse):
        payload = {
            "content": f"""Here's your Jubi Analysis:\nMatch Percent: {response.match_percent}\nApply? {"Yes" if response.apply else "No"}""",
        }
        try:
            ret = r.post(self.webhook, json=payload, timeout=10)
        except r.exceptions.RequestException as Error:
            raise Error

        self._post(response.analysis)

    def _post(self, content: str):
        DISCORD_CHARACTER_LIMIT = 2000
        for i in range(0, len(content), DISCORD_CHARACTER_LIMIT):
            ret = r.post(
                self.webhook,
                json={"content": content[i : i + DISCORD_CHARACTER_LIMIT]},
                timeout=10,
            )
            ret.raise_for_status()
