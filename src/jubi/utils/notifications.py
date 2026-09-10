import requests as r
import sys
import click
from pathlib import Path
from dotenv import load_dotenv 
import os

dotenv_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(dotenv_path=dotenv_path)

class Notifications:
    def __init__(self):
        
        config = os.getenv("WEBHOOK")
        if config is None:
            raise RuntimeError(
                f"WEBHOOK is missing. Expected it in {dotenv_path}"
            )
        self.webhook: str = config

    def update_notif(self, job_name, company):
        payload = {
            'content': f'An update to the position: {job_name} @ {company} was just made.',
        }
        try:
            ret = r.post(self.webhook, json=payload, timeout=10)
        except r.exceptions.RequestException as Error:
            click.echo("[ERROR] Could not connect to Discord. Please check your network connection or verify that the configured webhook is valid.")
    def add_notif(self, job, company):
        payload = {
            'content': f'A new job was added to Jubi! It\'s {job} @ {company}. Good Luck, Akli!',

        }
        try:
            ret = r.post(self.webhook, json=payload, timeout=10)
            click.echo("A job has been added to Jubi. A confirmation message has been sent to Discord!")
        except r.exceptions.RequestException as Error:
            click.echo("[ERROR] Could not connect to Discord. Please check your network connection or verify that the configured webhook is valid.")
            
            


        
    

                
                    