from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Job(BaseModel):
    source: str
    title: str
    client: Optional[str] = None
    url: str
    location: Optional[str] = None
    tags: list[str] = []
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    currency: Optional[str] = None
    posted_at: Optional[datetime] = None
    description: Optional[str] = None

    def dedup_key(self) -> str:
        return f"{self.source}:{self.url.strip().lower()}"
