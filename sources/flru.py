from flru import Client
from flru.models import ProjectSummary

from sources.models import Job

MAX_ATTEMPTS = 2


async def fetch_jobs(query: str, limit: int = 50) -> list[Job]:
    pages = max(1, limit // 20)
    projects: list[ProjectSummary] = []
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            async with Client() as fl:
                projects = await fl.projects(pages=pages, query=query, types="order")
            break
        except ValueError:
            if attempt == MAX_ATTEMPTS:
                raise
    jobs = []
    for project in projects[:limit]:
        jobs.append(
            Job(
                source="FL.ru",
                title=project.title,
                client=None,
                url=project.url,
                tags=[],
                budget_min=float(project.budget_min) if project.budget_min is not None else None,
                budget_max=getattr(project, "budget_max", None),
                currency=getattr(project, "currency", "RUB"),
                posted_at=getattr(project, "created_at", None),
                description=getattr(project, "description", None),
            )
        )
    return jobs
