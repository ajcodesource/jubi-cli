from pathlib import Path
from platformdirs import user_data_path
import shutil


class ResumeRepository:
    def __init__(self, base_path: Path | None = None):
        self.resume_path = (
            base_path if base_path else user_data_path("Jubi") / "resumes"
        )
        self.resume_path.mkdir(parents=True, exist_ok=True)

    # TODO add file
    def add_resume(self, resume: Path) -> bool:
        if resume.exists() and resume.is_file():
            shutil.copy(resume, self.resume_path)
            return True
        return False

    # TODO get files
    def get_resumes(self) -> list[Path]:
        return [
            resume
            for resume in self.resume_path.iterdir()
            if resume.is_file()
            and (
                resume.suffix.lower() == ".pdf"
                or resume.suffix.lower() == ".docx"
                or resume.suffix.lower() == ".doc"
            )
        ]
