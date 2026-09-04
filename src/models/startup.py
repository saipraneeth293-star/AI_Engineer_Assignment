from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Source(BaseModel):
    name: str
    url: str


class StartupContent(BaseModel):
    entityName: str
    employeeCount: Optional[int] = None
    website: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None


class Startup(BaseModel):
    schemaVersion: str = "1.0"
    recordType: str = "STARTUP"

    source: Source
    content: StartupContent

    collectedAt: str