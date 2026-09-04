from typing import Optional

from pydantic import BaseModel


class NewsSource(BaseModel):

    name: str

    url: str


class NewsContent(BaseModel):

    title: str

    articleUrl: str

    fullText: Optional[str] = None

    publishedAt: str

    author: Optional[str] = None


class NewsArticle(BaseModel):

    schemaVersion: str = "1.0"

    recordType: str = "NEWS"

    source: NewsSource

    content: NewsContent

    collectedAt: str