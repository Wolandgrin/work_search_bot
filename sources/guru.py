import re
from datetime import datetime, timedelta, timezone

import httpx

from sources.models import Job

GURU_JOBS_URL = "https://www.guru.com/d/jobs/"
GURU_JOBS_PAGE_URL = "https://www.guru.com/d/jobs/pg/{page}/"
HEADERS = {"User-Agent": "Mozilla/5.0"}
MAX_PAGES = 10

TITLE_RE = re.compile(r'<a v-pre href="(/jobs/[^"]+)">([^<]+)</a>')
POSTED_RE = re.compile(r'Posted\s*<strong>([^<]+)</strong>')

RELATIVE_TIME_UNITS = {
    "min": "minutes",
    "hr": "hours",
    "day": "days",
    "week": "weeks",
    "month": "days",
}


def _parse_relative_time(text: str) -> datetime | None:
    match = re.match(r"(\d+)\s*(min|hr|day|week|month)s?\s*ago", text.strip().lower())
    if not match:
        return None
    amount, unit = int(match.group(1)), match.group(2)
    if unit == "month":
        amount *= 30
    kwargs = {RELATIVE_TIME_UNITS[unit]: amount}
    return datetime.now(timezone.utc) - timedelta(**kwargs)


async def fetch_jobs(query: str, limit: int = 50) -> list[Job]:
    query_lower = query.lower() if query else ""
    jobs: list[Job] = []
    async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        page = 1
        while len(jobs) < limit and page <= MAX_PAGES:
            url = GURU_JOBS_URL if page == 1 else GURU_JOBS_PAGE_URL.format(page=page)
            response = await client.get(url)
            response.raise_for_status()
            records = response.text.split('class="record jobRecord"')[1:]
            if not records:
                break
            for record in records:
                title_match = TITLE_RE.search(record)
                if not title_match:
                    continue
                path, title = title_match.groups()
                title = title.strip()
                if query_lower and query_lower not in title.lower():
                    continue
                posted_match = POSTED_RE.search(record)
                posted_at = _parse_relative_time(posted_match.group(1)) if posted_match else None
                job_url = "https://www.guru.com" + path.split("&SearchUrl")[0]
                jobs.append(
                    Job(
                        source="Guru",
                        title=title,
                        url=job_url,
                        tags=[],
                        currency="USD",
                        posted_at=posted_at,
                    )
                )
                if len(jobs) >= limit:
                    break
            page += 1
    return jobs[:limit]
