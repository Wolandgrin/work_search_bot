from datetime import datetime, timezone

import httpx

from sources.models import Job

SEARCH_URL = "https://nofluffjobs.com/api/search/posting"
QUERY_PARAMS = {"salaryCurrency": "PLN", "salaryPeriod": "month"}
HEADERS = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
DEFAULT_CATEGORY = "testing"
MAX_PAGES = 5


def _extract_city(posting: dict) -> str | None:
    for place in posting.get("location", {}).get("places", []):
        city = place.get("city")
        if city and city != "Remote":
            return str(city)
    return None


def _build_tags(posting: dict) -> list[str]:
    return [
        tile["value"]
        for tile in posting.get("tiles", {}).get("values", [])
        if tile.get("type") == "requirement"
    ]


def _parse_posting(posting: dict, cities: set[str]) -> Job:
    salary = posting.get("salary") or {}
    posted_ms = posting.get("posted")
    posted_at = datetime.fromtimestamp(posted_ms / 1000, tz=timezone.utc) if posted_ms else None
    location = ", ".join(sorted(cities)) if cities else ("Remote" if posting.get("fullyRemote") else None)
    return Job(
        source="NoFluffJobs",
        title=posting.get("title", ""),
        client=posting.get("name"),
        url=f"https://nofluffjobs.com/job/{posting['id']}",
        location=location,
        tags=_build_tags(posting),
        budget_min=salary.get("from"),
        budget_max=salary.get("to"),
        currency=salary.get("currency"),
        posted_at=posted_at,
    )


async def fetch_jobs(query: str, limit: int = 50) -> list[Job]:
    body_base: dict = {"criteriaSearch": {"category": [DEFAULT_CATEGORY]}, "rawSearch": query or ""}
    postings_by_reference: dict[str, dict] = {}
    cities_by_reference: dict[str, set[str]] = {}
    order: list[str] = []
    async with httpx.AsyncClient(headers=HEADERS, timeout=15) as client:
        for page in range(1, MAX_PAGES + 1):
            if len(order) >= limit:
                break
            response = await client.post(
                SEARCH_URL, params=QUERY_PARAMS, json={"page": page, **body_base}
            )
            response.raise_for_status()
            payload = response.json()
            postings = payload.get("postings", [])
            if not postings:
                break
            for posting in postings:
                reference = posting.get("reference") or posting["id"]
                city = _extract_city(posting)
                if reference not in postings_by_reference:
                    postings_by_reference[reference] = posting
                    cities_by_reference[reference] = set()
                    order.append(reference)
                if city:
                    cities_by_reference[reference].add(city)
            if page >= payload.get("totalPages", page):
                break
    jobs = [
        _parse_posting(postings_by_reference[reference], cities_by_reference[reference])
        for reference in order[:limit]
    ]
    return jobs
