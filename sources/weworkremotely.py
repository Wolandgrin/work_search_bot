from datetime import timezone
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from sources.models import Job

WWR_RSS_URL = "https://weworkremotely.com/remote-jobs.rss"


async def fetch_jobs(query: str, limit: int = 50) -> list[Job]:
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(WWR_RSS_URL)
        response.raise_for_status()
        feed = feedparser.parse(response.text)
    query_lower = query.lower()
    jobs = []
    for entry in feed.entries:
        raw_title = entry.get("title", "")
        summary = entry.get("summary", "")
        haystack = f"{raw_title} {summary}".lower()
        if query_lower and query_lower not in haystack:
            continue
        client_name, _, position = raw_title.partition(":")
        posted_at = None
        if entry.get("published"):
            try:
                posted_at = parsedate_to_datetime(entry["published"]).astimezone(timezone.utc)
            except (TypeError, ValueError):
                posted_at = None
        jobs.append(
            Job(
                source="WeWorkRemotely",
                title=position.strip() or raw_title,
                client=client_name.strip() if position else None,
                url=entry.get("link", ""),
                tags=[t.term for t in entry.get("tags", [])] if entry.get("tags") else [],
                currency=None,
                posted_at=posted_at,
                description=summary,
            )
        )
        if len(jobs) >= limit:
            break
    return jobs
