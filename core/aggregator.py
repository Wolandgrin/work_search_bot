import asyncio
import logging
from datetime import datetime, timezone

from core.filters import filter_jobs
from sources import flru, freelancehunt, guru, jobscz, kwork, remoteok, remotive, weworkremotely
from sources.models import Job

logger = logging.getLogger(__name__)
EPOCH_START = datetime.min.replace(tzinfo=timezone.utc)

SOURCE_ADAPTERS = {
    "remotive": remotive.fetch_jobs,
    "remoteok": remoteok.fetch_jobs,
    "weworkremotely": weworkremotely.fetch_jobs,
    "flru": flru.fetch_jobs,
    "kwork": kwork.fetch_jobs,
    "guru": guru.fetch_jobs,
    "freelancehunt": freelancehunt.fetch_jobs,
    "jobscz": jobscz.fetch_jobs,
}


async def _fetch_from_source(name: str, query: str, limit: int) -> list[Job]:
    fetch_fn = SOURCE_ADAPTERS[name]
    try:
        return await fetch_fn(query, limit)
    except Exception:
        logger.exception("Source %s failed", name)
        return []


async def search_jobs(
    query: str,
    sources: list[str] | None = None,
    limit_per_source: int = 30,
    keywords: list[str] | None = None,
) -> list[Job]:
    active_sources = sources or list(SOURCE_ADAPTERS.keys())
    tasks = [
        _fetch_from_source(name, query, limit_per_source)
        for name in active_sources
        if name in SOURCE_ADAPTERS
    ]
    results = await asyncio.gather(*tasks)
    all_jobs: list[Job] = [job for group in results for job in group]
    filtered = filter_jobs(all_jobs, keywords) if keywords else all_jobs
    seen = set()
    deduped = []
    for job in filtered:
        key = job.dedup_key()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(job)
    deduped.sort(key=lambda j: j.posted_at or EPOCH_START, reverse=True)
    return deduped
