import html
import re

import httpx

from sources.models import Job

SEARCH_URL = "https://justjoin.it/job-offers/all-locations/testing"
HEADERS = {"User-Agent": "Mozilla/5.0"}

CARD_SPLIT_RE = re.compile(r'<li class="MuiBox-root [\w-]+" data-index="\d+">')
TITLE_RE = re.compile(
    r'<a href="(https://justjoin\.it/job-offer/[^"]+)"\s+title="View offer[^"]*"'
    r'\s+class="offer_list_offer_title_link">([^<]+)</a>'
)
WORKPLACE_RE = re.compile(r'<p class="[\w-]+">(Remote|Hybrid|Office|Fully remote)</p>')
SALARY_RE = re.compile(r'<span class="[\w-]+">([\d,.\s\u2013-]+)</span><span class="[\w-]+">([A-Za-z/]+)</span>')
TAGS_BLOCK_RE = re.compile(r'<div class="MuiBox-root [\w-]+">((?:<div class="MuiBox-root [\w-]+">[^<]+</div>){1,10})</div>')
TAG_RE = re.compile(r'<div class="MuiBox-root [\w-]+">([^<]+)</div>')


def _parse_card(block: str) -> Job | None:
    title_match = TITLE_RE.search(block)
    if not title_match:
        return None
    url, raw_title = title_match.groups()
    workplace_match = WORKPLACE_RE.search(block)
    salary_match = SALARY_RE.search(block)
    tags_match = TAGS_BLOCK_RE.search(block)
    budget_min = budget_max = None
    currency = None
    if salary_match:
        salary_text, currency = salary_match.groups()
        parts = [p.strip().replace(",", ".").replace(" ", "") for p in salary_text.split("-")]
        try:
            if len(parts) == 2:
                budget_min, budget_max = float(parts[0]), float(parts[1])
            elif len(parts) == 1:
                budget_min = budget_max = float(parts[0])
        except ValueError:
            pass
    tags = TAG_RE.findall(tags_match.group(1)) if tags_match else []
    return Job(
        source="JustJoin.it",
        title=html.unescape(raw_title),
        url=url,
        location=workplace_match.group(1) if workplace_match else None,
        tags=[html.unescape(t) for t in tags],
        budget_min=budget_min,
        budget_max=budget_max,
        currency=currency,
    )


async def fetch_jobs(query: str, limit: int = 50) -> list[Job]:
    async with httpx.AsyncClient(headers=HEADERS, timeout=15, follow_redirects=True) as client:
        response = await client.get(SEARCH_URL)
        response.raise_for_status()
    text = response.text.replace("<!-- -->", "")
    blocks = CARD_SPLIT_RE.split(text)[1:]
    jobs: list[Job] = []
    query_lower = query.lower()
    for block in blocks:
        job = _parse_card(block)
        if not job:
            continue
        if query_lower and query_lower not in job.title.lower():
            continue
        jobs.append(job)
        if len(jobs) >= limit:
            break
    return jobs
