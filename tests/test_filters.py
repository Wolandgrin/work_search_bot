"""Регрессионные тесты политики локации/режима работы (core.filters).

Цель: гибрид/on-site вне доступной локации (напр. Польша) отсеивается,
remote и вакансии в Чехии — остаются. См. passes_location_policy.
"""
import pytest

from core.filters import filter_jobs, passes_location_policy
from sources.models import Job


def _job(source: str, location=None, tags=None, title="QA Automation Engineer") -> Job:
    return Job(source=source, title=title, url=f"https://example.com/{source}", location=location, tags=tags or [])


@pytest.mark.parametrize(
    "source, location, tags, expected",
    [
        # Польские доски: только remote.
        ("JustJoin.it", "Hybrid", None, False),
        ("JustJoin.it", "Office", None, False),
        ("JustJoin.it", "Remote", None, True),
        ("JustJoin.it", "Fully remote", None, True),
        ("NoFluffJobs", "Warszawa, Kraków", None, False),
        ("NoFluffJobs", "Remote", None, True),
        ("NoFluffJobs", "Gdansk", ["Remote"], True),  # remote-маркер в тегах
        # LinkedIn (глобальный): remote ИЛИ явная Чехия.
        ("LinkedIn", "Warsaw, Masovian, Poland", None, False),
        ("LinkedIn", "Berlin, Germany", None, False),
        ("LinkedIn", "Prague, Czechia", None, True),
        ("LinkedIn", "European Union (Remote)", None, True),
        ("LinkedIn", None, None, True),  # неизвестная локация не режется
        # Доверенные источники (чешские + remote/фриланс): оставляем всё.
        ("Jobs.cz", "Liberec", None, True),
        ("StartupJobs.cz", "Olomouc", None, True),
        ("RemoteOK", None, None, True),
        ("FL.ru", None, None, True),
    ],
)
def test_passes_location_policy(source, location, tags, expected):
    assert passes_location_policy(_job(source, location, tags)) is expected


def test_filter_jobs_drops_poland_hybrid_keeps_remote_and_cz():
    jobs = [
        _job("JustJoin.it", "Hybrid"),          # drop
        _job("NoFluffJobs", "Warszawa"),         # drop
        _job("JustJoin.it", "Remote"),           # keep
        _job("LinkedIn", "Prague, Czechia"),     # keep
        _job("Jobs.cz", "Brno"),                 # keep
    ]
    kept = filter_jobs(jobs, keywords=["qa"])
    kept_pairs = {(j.source, j.location) for j in kept}
    assert ("JustJoin.it", "Hybrid") not in kept_pairs
    assert ("NoFluffJobs", "Warszawa") not in kept_pairs
    assert ("JustJoin.it", "Remote") in kept_pairs
    assert ("LinkedIn", "Prague, Czechia") in kept_pairs
    assert ("Jobs.cz", "Brno") in kept_pairs
