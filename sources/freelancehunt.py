from datetime import datetime

import httpx

from sources.models import Job

API_URL = "https://api.freelancehunt.com/v2/projects"


async def fetch_jobs(query: str, limit: int = 50) -> list[Job]:
    # Anonymous access (no API token) only exposes the ~10 most recent
    # public projects; pagination requires an authenticated token.
    query_lower = query.lower() if query else ""
    jobs = []
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(API_URL)
        response.raise_for_status()
        payload = response.json()
    for item in payload.get("data", []):
        attrs = item["attributes"]
        title = attrs.get("name") or ""
        if query_lower and query_lower not in title.lower():
            continue
        budget = attrs.get("budget") or {}
        published_at = attrs.get("published_at")
        posted_at = datetime.fromisoformat(published_at) if published_at else None
        jobs.append(
            Job(
                source="FreelanceHunt",
                title=title,
                client=attrs.get("employer", {}).get("login"),
                url=item["links"]["self"]["web"],
                tags=[skill["name"] for skill in attrs.get("skills", [])],
                budget_min=budget.get("amount"),
                currency=budget.get("currency"),
                posted_at=posted_at,
                description=attrs.get("description"),
            )
        )
        if len(jobs) >= limit:
            break
    return jobs
