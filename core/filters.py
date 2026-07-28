from sources.models import Job

DEFAULT_KEYWORDS = [
    "qa",
    "quality assurance",
    "test automation",
    "selenium",
    "playwright",
    "pytest",
    "тестирование",
    "тестировщик",
    "автотест",
]


MAX_TRUSTED_TAGS = 10
MIN_DESCRIPTION_MATCHES = 2


def matches_keywords(job: Job, keywords: list[str]) -> bool:
    lowered_keywords = [keyword.lower() for keyword in keywords]
    trusted_tags = job.tags if len(job.tags) <= MAX_TRUSTED_TAGS else []
    title_and_tags = " ".join([job.title, " ".join(trusted_tags)]).lower()
    if any(keyword in title_and_tags for keyword in lowered_keywords):
        return True
    description = (job.description or "").lower()
    description_matches = sum(1 for keyword in lowered_keywords if keyword in description)
    return description_matches >= MIN_DESCRIPTION_MATCHES


def filter_jobs(jobs: list[Job], keywords: list[str] | None = None) -> list[Job]:
    active_keywords = keywords or DEFAULT_KEYWORDS
    return [job for job in jobs if matches_keywords(job, active_keywords)]
