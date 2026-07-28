---
trigger: always_on
description:
globs:
---

# Tasks — freelance_search

## Active Tasks

- [ ] Протестировать MCP-сервер из Windsurf/Cascade (subprocess stdio)

## Backlog

- [ ] Upwork: ПРОВЕРЕНО (2026-07-27) — Cloudflare Turnstile блокирует Playwright/CDP-браузер сразу на логине, даже в ручном режиме. Обход только через stealth-патчи + residential-прокси (нарушение ToS, риск бана). Официальный API требует OAuth-партнёрство. Отложено.
- [ ] Fiverr: ПРОВЕРЕНО (2026-07-27) — логин-форма изначально доступна, но после нескольких попыток PerimeterX задетектил автоматизацию и заблокировал профиль/IP. Дальнейшие попытки не предпринимать — риск бана аккаунта. Отложено.
- [ ] Toptal: НЕВОЗМОЖНО через логин/пароль — закрытая vetted-сеть без публичной биржи, доступ только после ручного скрининга (3-8 недель)
- [ ] Freelancer.com: пользователь сообщил, что генерация personal access token потребовала оплату/верификацию на его аккаунте — отложено
- [ ] Habr Freelance (freelance.habr.com): ПРОВЕРЕНО (2026-07-27) — сервис закрыт (404 Gone), недоступен
- [ ] Weblancer.net: ПРОВЕРЕНО (2026-07-27) — Cloudflare блокирует даже обычные HTTP-запросы (403, cf-mitigated: challenge), нужен полноценный браузер — отложено
- [ ] uTest/Applause/Testlio (краудтестинг): ПРОВЕРЕНО (2026-07-27) — нет публичного списка проектов; вакансии доступны только после регистрации + прохождения onboarding (uTest Academy), матчинг через приглашения на email — не скрейпится напрямую, отложено
- [ ] Фильтрация по зарплате / бюджету

## Архитектура (реализовано)

```
sources/models.py            # Job (pydantic)
sources/remotive.py          # free API
sources/remoteok.py          # free API, client-side filter
sources/weworkremotely.py    # RSS
sources/flru.py              # flru-parser (scraping публичных страниц, без авторизации)
sources/kwork.py             # kworker (pip), login KWORK_LOGIN/KWORK_PASSWORD, категория 81 "Юзабилити, тесты и помощь"
sources/guru.py              # scraping guru.com/d/jobs/ (публично, без авторизации, regex-парсинг HTML)
sources/freelancehunt.py     # api.freelancehunt.com/v2/projects — публично, без токена, но только ~10 последних проектов (пагинация требует токен)
sources/jobscz.py            # jobs.cz — постоянные вакансии (QA Lead/Automation QA/SDET и т.д. в Чехии), server-rendered HTML, без авторизации, мультизапросы по DEFAULT_QUERIES
core/filters.py              # DEFAULT_KEYWORDS: qa, quality assurance, test automation, selenium, playwright, pytest,
                              # тестирование, тестировщик, автотест
                              # matches_keywords: title/tags(≤10) точное ИЛИ ≥2 keyword в description (MIN_DESCRIPTION_MATCHES)
core/aggregator.py           # search_jobs() — параллельный fetch + dedup (по url, не по title!) + сортировка по дате
core/storage.py              # SeenJobsStore (SQLite, seen_jobs.db) — дедуп между запусками бота
main.py                      # FastMCP server, tool: search_freelance_jobs(query, sources, limit_per_source, keywords)
bot/notifier.py               # TelegramNotifier — sendMessage (без polling, чтобы не конфликтовать с binScalp bot)
bot/scheduler.py              # APScheduler, интервал 15 мин, poll_and_notify()
bot/run_bot.py                 # entrypoint: python -m bot.run_bot
```

Бот @bybit_scalpingbot (общий с binScalp, используется только sendMessage, без getUpdates/polling).
TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID / KWORK_LOGIN / KWORK_PASSWORD в `.env` (в .gitignore, не коммитить).

ВАЖНО: пакет `kwork` (PyPI) требует pydantic<2.0 и ЛОМАЕТ проект — использовать только `kworker` (pydantic>=2.11).

Проверено вручную (2026-07-28): 8 источников (Remotive/RemoteOK/WWR/FL.ru/Kwork/Guru/FreelanceHunt/Jobs.cz) отдают данные, бот в фоне шлёт сообщения в Telegram. Jobs.cz добавлен как источник постоянных вакансий (QA Lead/Automation QA/SDET) в Чехии — 25 вакансий разослано в первом прогоне.

ВАЖНО: исправлен баг дедупликации — `Job.dedup_key()` раньше использовал `title.lower()`, из-за чего разные вакансии с одинаковым названием у разных работодателей (частое явление на jobs.cz) схлопывались в одну. Теперь дедуп по `url`.

## Notes

Проект стартовал 2026-07-27. См. `mcp_servers.md` для существующих MCP-инструментов.
