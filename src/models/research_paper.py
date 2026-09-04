from typing import Optional
from pydantic import BaseModel


class ResearchPaper(BaseModel):

    schemaVersion: str = "1.0"
    recordType: str = "RESEARCH_PAPER"

    title: str
    authors: list[str]

    paper_url: str

    github_url: Optional[str] = None
    github_stars: Optional[int] = None

    published_date: str