import logging
import os
from datetime import datetime, timezone

from kworker import KworkAPI

from sources.models import Job

logger = logging.getLogger(__name__)

TESTING_CATEGORY_ID = 81
PROJECT_URL_TEMPLATE = "https://kwork.ru/projects/{id}/view"


async def fetch_jobs(query: str, limit: int = 30) -> list[Job]:
    login = os.environ.get("KWORK_LOGIN")
    password = os.environ.get("KWORK_PASSWORD")
    if not login or not password:
        logger.warning("KWORK_LOGIN/KWORK_PASSWORD not set, skipping Kwork")
        return []

    client = KworkAPI(login=login, password=password)
    try:
        projects = await client.get_projects(
            categories_ids=[TESTING_CATEGORY_ID],
            query=query or None,
            page=1,
        )
    finally:
        await client.close()

    jobs = []
    for p in projects[:limit]:
        posted_at = None
        if p.date_confirm:
            posted_at = datetime.fromtimestamp(p.date_confirm, tz=timezone.utc)
        jobs.append(
            Job(
                source="Kwork",
                title=p.title or "",
                client=p.username,
                url=PROJECT_URL_TEMPLATE.format(id=p.id),
                tags=[],
                budget_min=p.price,
                currency="RUB",
                posted_at=posted_at,
                description=p.description,
            )
        )
    return jobs
