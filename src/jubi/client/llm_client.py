from jubi.core.models.ResumeAnalysis import ResumeModelResponse
from dotenv import load_dotenv
import os
from google import genai
from pathlib import Path


class LLM_Client:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API")
        self.gemini = genai.Client(api_key=self.api_key)
        self.prompt = Path(__file__).parent.resolve() / "prompt.md"

    def send_prompt(self, resume_string: str, job_description: str):

        with open(self.prompt, "r") as system_prompt:
            prompt_string = system_prompt.read()
        final_prompt = prompt_string.format(
            resume=resume_string, description=job_description
        )

        interaction = self.gemini.interactions.create(
            model="gemini-3.8-flash",
            input=final_prompt,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": ResumeModelResponse.model_json_schema(),
            },
        )
        res = interaction.output_text
        if res is None:
            raise ValueError("LLM interaction returned no output")

        return ResumeModelResponse.model_validate_json(res)
