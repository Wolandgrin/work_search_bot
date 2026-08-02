from datetime import datetime, timezone

import httpx

from sources.models import Job

REMOTEOK_API_URL = "https://remoteok.com/api"
USER_AGENT = "Mozilla/5.0 (compatible; freelance-search-mcp/1.0)"


async def fetch_jobs(query: str, limit: int = 50) -> list[Job]:
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=30, headers=headers) as client:
        response = await client.get(REMOTEOK_API_URL)
        response.raise_for_status()
        payload = response.json()
    query_lower = query.lower()
    jobs = []
    for item in payload:
        if "id" not in item:
            continue
        title = item.get("position", "")
        description = item.get("description", "")
        tags = item.get("tags", [])
        haystack = " ".join([title, description] + tags).lower()
        if query_lower and query_lower not in haystack:
            continue
        posted_at = None
        if item.get("date"):
            posted_at = datetime.fromisoformat(item["date"]).astimezone(timezone.utc)
        jobs.append(
            Job(
                source="RemoteOK",
                title=title,
                client=item.get("company"),
                url=item.get("url", f"https://remoteok.com/remote-jobs/{item['id']}"),
                tags=tags,
                budget_min=item.get("salary_min"),
                budget_max=item.get("salary_max"),
                currency="USD",
                posted_at=posted_at,
                description=description,
            )
        )
        if len(jobs) >= limit:
            break
    return jobs
