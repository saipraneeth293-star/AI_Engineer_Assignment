from typing import Optional

from pydantic import BaseModel


class JobSource(BaseModel):

    name: str

    url: str


class JobContent(BaseModel):

    title: str

    company: str

    jobUrl: str

    date: str

    is_remote: bool = False

    role_family: str = "Other"

    location: Optional[str] = None

    description: Optional[str] = None


class Job(BaseModel):

    schemaVersion: str = "1.0"

    recordType: str = "JOB"

    source: JobSource

    content: JobContent

    collectedAt: str