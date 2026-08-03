import html
import re
from datetime import datetime, timezone

import httpx

from sources.models import Job

# NOTE: uses LinkedIn's public (no-login) "guest" job search endpoint, which is
# outside the official API and technically against LinkedIn's ToS (gray zone,
# see hiQ Labs v. LinkedIn on the legality of scraping public data). Kept to a
# single low-frequency request per poll (one query, 10 results) to minimize
# the risk of the VM's IP getting soft-blocked (HTTP 429/999).
SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
DEFAULT_KEYWORDS_QUERY = 'QA OR "test automation" OR "QA lead" OR "QA architect" OR SDET'
DEFAULT_LOCATION = "Prague, Czechia"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

URL_RE = re.compile(r'<a class="base-card__full-link[^"]*"[^>]*href="([^"?]+)')
TITLE_RE = re.compile(r'<h3 class="base-search-card__title">\s*([^\n<]+?)\s*</h3>')
COMPANY_RE = re.compile(r'<h4 class="base-search-card__subtitle">[\s\S]*?>\s*([^\n<]+?)\s*</a>')
LOCATION_RE = re.compile(r'<span class="job-search-card__location">\s*([^\n<]+?)\s*</span>')
DATE_RE = re.compile(r'datetime="(\d{4}-\d{2}-\d{2})"')


def _parse_chunk(chunk: str) -> Job | None:
    url_match = URL_RE.search(chunk)
    title_match = TITLE_RE.search(chunk)
    if not url_match or not title_match:
        return None
    company_match = COMPANY_RE.search(chunk)
    location_match = LOCATION_RE.search(chunk)
    date_match = DATE_RE.search(chunk)
    posted_at = None
    if date_match:
        posted_at = datetime.strptime(date_match.group(1), "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return Job(
        source="LinkedIn",
        title=html.unescape(title_match.group(1)),
        client=html.unescape(company_match.group(1)) if company_match else None,
        url=url_match.group(1),
        location=html.unescape(location_match.group(1)) if location_match else None,
        posted_at=posted_at,
    )


async def fetch_jobs(query: str, limit: int = 10) -> list[Job]:
    params = {
        "keywords": query or DEFAULT_KEYWORDS_QUERY,
        "location": DEFAULT_LOCATION,
        "start": "0",
    }
    async with httpx.AsyncClient(headers=HEADERS, timeout=30) as client:
        response = await client.get(SEARCH_URL, params=params)
        response.raise_for_status()
        body = response.text
    jobs: list[Job] = []
    for chunk in body.split('data-entity-urn="urn:li:jobPosting:')[1:]:
        job = _parse_chunk(chunk)
        if job:
            jobs.append(job)
        if len(jobs) >= limit:
            break
    return jobs
