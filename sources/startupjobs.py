import re

import httpx

from core.filters import DEFAULT_KEYWORDS, matches_keywords
from sources.models import Job

BASE_URL = "https://www.startupjobs.cz/api/offers"
DETAIL_BASE_URL = "https://www.startupjobs.cz"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_PAGES = 25
HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(text: str) -> str:
    return HTML_TAG_RE.sub(" ", text).strip()


def _parse_offer(item: dict) -> Job:
    salary = item.get("salary") or {}
    location = item.get("locations") or ("Remote" if item.get("isRemote") else None)
    return Job(
        source="StartupJobs.cz",
        title=item.get("name", ""),
        client=item.get("company"),
        url=f"{DETAIL_BASE_URL}{item['url']}",
        location=location,
        tags=item.get("areaNames", []),
        budget_min=salary.get("min"),
        budget_max=salary.get("max"),
        currency=salary.get("currency"),
        description=_strip_html(item.get("description", "")),
    )


async def fetch_jobs(query: str, limit: int = 50) -> list[Job]:
    keywords = [query] if query else DEFAULT_KEYWORDS
    jobs: list[Job] = []
    async with httpx.AsyncClient(headers=HEADERS, timeout=30) as client:
        page = 1
        while page <= MAX_PAGES:
            response = await client.get(BASE_URL, params={"page": page})
            response.raise_for_status()
            payload = response.json()
            offers = payload.get("resultSet", [])
            if not offers:
                break
            for item in offers:
                job = _parse_offer(item)
                if matches_keywords(job, keywords):
                    jobs.append(job)
                    if len(jobs) >= limit:
                        return jobs
            paginator = payload.get("paginator", {})
            if page >= paginator.get("max", page):
                break
            page += 1
    return jobs
