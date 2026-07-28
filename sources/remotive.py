from datetime import datetime, timezone

import httpx

from sources.models import Job

REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"


async def fetch_jobs(query: str, limit: int = 50) -> list[Job]:
    params: dict[str, str | int] = {"search": query, "limit": limit}
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(REMOTIVE_API_URL, params=params)
        response.raise_for_status()
        payload = response.json()
    jobs = []
    for item in payload.get("jobs", []):
        posted_at = None
        if item.get("publication_date"):
            raw_date = item["publication_date"].replace("Z", "+00:00")
            posted_at = datetime.fromisoformat(raw_date)
            if posted_at.tzinfo is None:
                posted_at = posted_at.replace(tzinfo=timezone.utc)
        jobs.append(
            Job(
                source="Remotive",
                title=item.get("title", ""),
                client=item.get("company_name"),
                url=item.get("url", ""),
                tags=item.get("tags", []),
                currency=None,
                posted_at=posted_at,
                description=item.get("description"),
            )
        )
    return jobs[:limit]
