import html
import re

import httpx

from sources.models import Job

BASE_URL = "https://www.jobs.cz/prace/"
DEFAULT_QUERIES = ["QA Engineer", "QA Lead", "test automation", "SDET"]
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_PAGES = 3

TITLE_RE = re.compile(r'data-test-ad-title="([^"]+)"')
URL_RE = re.compile(r'href="(https://www\.jobs\.cz/rpd/[^"]+)"')
JOBAD_ID_RE = re.compile(r'data-jobad-id="(\d+)"')
COMPANY_RE = re.compile(r'<span translate="no">([^<]+)</span>')
LOCATION_RE = re.compile(r'data-test="serp-locality"[\s\S]*?</svg>\s*([^\n<]+?)\s*</li>')


async def _fetch_query(
    client: httpx.AsyncClient, query: str, limit: int, seen_ids: set[str]
) -> list[Job]:
    jobs: list[Job] = []
    page = 1
    while len(jobs) < limit and page <= MAX_PAGES:
        params = {"q[]": query}
        if page > 1:
            params["page"] = str(page)
        response = await client.get(BASE_URL, params=params)
        response.raise_for_status()
        articles = response.text.split('class="SearchResultCard"')[1:]
        if not articles:
            break
        for article in articles:
            title_match = TITLE_RE.search(article)
            url_match = URL_RE.search(article)
            id_match = JOBAD_ID_RE.search(article)
            if not title_match or not url_match or not id_match:
                continue
            job_id = id_match.group(1)
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)
            company_match = COMPANY_RE.search(article)
            location_match = LOCATION_RE.search(article)
            jobs.append(
                Job(
                    source="Jobs.cz",
                    title=html.unescape(title_match.group(1)),
                    client=html.unescape(company_match.group(1)) if company_match else None,
                    url=f"https://www.jobs.cz/rpd/{job_id}/",
                    location=html.unescape(location_match.group(1)) if location_match else None,
                    currency="CZK",
                )
            )
            if len(jobs) >= limit:
                break
        page += 1
    return jobs


async def fetch_jobs(query: str, limit: int = 50) -> list[Job]:
    queries = [query] if query else DEFAULT_QUERIES
    per_query_limit = max(1, limit // len(queries)) if len(queries) > 1 else limit
    jobs = []
    seen_ids: set[str] = set()
    async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        for q in queries:
            jobs.extend(await _fetch_query(client, q, per_query_limit, seen_ids))
            if len(jobs) >= limit:
                break
    return jobs[:limit]
