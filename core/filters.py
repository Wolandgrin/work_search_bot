from sources.models import Job

DEFAULT_KEYWORDS = [
    "qa",
    "qa lead",
    "qa architect",
    "quality assurance",
    "test automation",
    "test lead",
    "test architect",
    "test manager",
    "qa team lead",
    "automation lead",
    "automation architect",
    "sdet",
    "ci/cd",
    "selenium",
    "webdriver",
    "playwright",
    "pytest",
    "тестирование",
    "тестировщик",
    "автотест",
]


MAX_TRUSTED_TAGS = 10
MIN_DESCRIPTION_MATCHES = 2


# --- Политика локации / режима работы -----------------------------------
# Пользователь в Праге: подходит remote или присутствие в Чехии; hybrid/
# on-site в другой стране (напр. Польша) не нужен — туда надо ездить.
#
# Фильтруем ПО ИСТОЧНИКУ, а не по списку городов: чешские доски отдают
# города ЧР (Liberec/Olomouc/...), которые трудно перечислить без ложных
# отсевов; польские — оставляем только удалёнку.

# Источники, локацию которых принимаем как есть: remote/фриланс-доски
# и чешские доски (внутренние вакансии Праги/ЧР — доступны или remote).
LOCATION_TRUSTED_SOURCES = {
    "FL.ru",
    "FreelanceHunt",
    "Guru",
    "Kwork",
    "RemoteOK",
    "Remotive",
    "WeWorkRemotely",
    "Jobs.cz",
    "StartupJobs.cz",
}

# Польские доски: оставляем только удалёнку.
REMOTE_ONLY_SOURCES = {"JustJoin.it", "NoFluffJobs"}

REMOTE_MARKERS = (
    "remote",
    "fully remote",
    "zdaln",  # zdalna/zdalnie (pl)
    "worldwide",
    "anywhere",
    "home office",
)

# Маркеры допустимого on-site (Чехия) — для глобальных источников (LinkedIn).
ACCEPTABLE_ONSITE_MARKERS = (
    "prague",
    "praha",
    "brno",
    "ostrava",
    "plzen",
    "plze\u0148",
    "liberec",
    "olomouc",
    "czech",
    "czechia",
    "\u010desk",  # Česká/Česko
    "cesk",
)


def _location_text(job: Job) -> str:
    loc = job.location
    if loc is None:
        return ""
    if isinstance(loc, (list, tuple)):
        loc = ", ".join(str(x) for x in loc)
    return str(loc).lower()


def _is_remote(job: Job) -> bool:
    text = _location_text(job)
    if any(marker in text for marker in REMOTE_MARKERS):
        return True
    tag_text = " ".join(job.tags).lower()
    return any(marker in tag_text for marker in REMOTE_MARKERS)


def passes_location_policy(job: Job) -> bool:
    """Отсеивает hybrid/on-site вне доступной локации (Чехия/remote).

    - Доверенные источники (remote/фриланс + чешские) — оставляем всё.
    - Польские доски — только remote.
    - Прочие (LinkedIn и т.п.) — remote ИЛИ явная Чехия; неизвестную
      локацию (location=None) не режем, чтобы не терять валидные вакансии.
    """
    if job.source in LOCATION_TRUSTED_SOURCES:
        return True
    if _is_remote(job):
        return True
    if job.source in REMOTE_ONLY_SOURCES:
        return False  # польская доска, не remote -> присутствие в Польше
    text = _location_text(job)
    if not text:
        return True  # локация неизвестна — не отсеиваем
    return any(marker in text for marker in ACCEPTABLE_ONSITE_MARKERS)


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
    return [
        job
        for job in jobs
        if matches_keywords(job, active_keywords) and passes_location_policy(job)
    ]
