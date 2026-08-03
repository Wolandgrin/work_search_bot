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
sources/flru.py              # flru-parser (scraping публичных страниц, без авторизации), retry при ValueError из-за бага flru.proxy.ProxyPool
sources/kwork.py             # ОТКЛЮЧЁН, не зарегистрирован в aggregator.py — требует российский паспорт, недоступен пользователю
sources/guru.py              # scraping guru.com/d/jobs/ (публично, без авторизации, regex-парсинг HTML), timeout=30
sources/freelancehunt.py     # api.freelancehunt.com/v2/projects — публично, без токена, но только ~10 последних проектов (пагинация требует токен)
sources/jobscz.py            # jobs.cz — постоянные вакансии (QA Lead/Automation QA/SDET и т.д. в Чехии), server-rendered HTML, без авторизации, мультизапросы по DEFAULT_QUERIES
sources/nofluffjobs.py       # POST nofluffjobs.com/api/search/posting, category=testing, ~1200 вакансий (в основном Польша), дедуп по polnstyu `reference` (без этого одна вакансия дублируется по регионам)
sources/justjoin.py          # justjoin.it/job-offers/all-locations/testing — данные рендерятся в SSR HTML (React), regex-парсинг, Плайврайт не потребовался, ~100 вакансий/запрос, ~34% с зарплатой
sources/startupjobs.py       # www.startupjobs.cz/api/offers — публичный JSON, но keyword/limit параметры сервер игнорирует (всегда отдаёт полный список ~410 вакансий постранично, 20/стр); фильтрация по DEFAULT_KEYWORDS внутри адаптера ДО обрезки по limit
sources/linkedin.py          # linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search — публичный guest-эндпоинт без логина, 1 запрос/poll (10 результатов), location="Prague, Czechia" (свободный текст "Czech Republic" резолвится в Доминиканскую Республику — баг геокодера LinkedIn, использовать только "Prague, Czechia"), серая зона ToS, риск блокировки IP при частых запросах
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
TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID в `.env` (в .gitignore, не коммитить).

ВАЖНО: пакет `kwork` (PyPI) требует pydantic<2.0 и ЛОМАЕТ проект — использовать только `kworker` (pydantic>=2.11). С 2026-08-02 источник kwork отключён вообще (требует российский паспорт, у пользователя его нет).

Проверено вручную (2026-07-28): 8 источников (Remotive/RemoteOK/WWR/FL.ru/Kwork/Guru/FreelanceHunt/Jobs.cz) отдают данные, бот в фоне шлёт сообщения в Telegram. Jobs.cz добавлен как источник постоянных вакансий (QA Lead/Automation QA/SDET) в Чехии — 25 вакансий разослано в первом прогоне.

ВАЖНО: исправлен баг дедупликации — `Job.dedup_key()` раньше использовал `title.lower()`, из-за чего разные вакансии с одинаковым названием у разных работодателей (частое явление на jobs.cz) схлопывались в одну. Теперь дедуп по `url`.

Изменения 2026-08-02:
- Kwork отключён (требует российский паспорт, недоступен пользователю).
- Добавлен NoFluffJobs (`sources/nofluffjobs.py`) — API `nofluffjobs.com/api/search/posting`, category=testing. Обнаружен и исправлен баг: одна вакансия возвращалась как десятки дублей (отдельная запись на каждый регион), все с одинаковым `reference` — теперь дедуп по этому полю внутри источника, а города собираются в одно поле location. `region`/`regions` параметры API не работают (всегда возвращает Польшу), поэтому фильтрация только по ключевым словам как у остальных широких источников.
- Добавлен JustJoin.it (`sources/justjoin.py`). Старый API (`api.justjoin.it`) мёртв. Реверс показал: данные рендерятся сервером прямо в HTML (Next.js SSR) на `justjoin.it/job-offers/all-locations/testing`, поэтому Playwright не потребовался — обычный httpx GET + regex-парсинг (как jobscz.py). ~100 вакансий за запрос, зарплата в EUR/h или EUR/day у ~34%.
- Исправлены intermittent ошибки на VM: `remoteok`/`guru` timeout 15→30с (`httpx.ReadTimeout`); `flru` — retry на `ValueError: min() iterable argument is empty` (баг в `flru.proxy.ProxyPool.acquire()`, внутри сторонней библиотеки, не исправлен в источнике, только обойдён).
- Установлены Playwright + chromium для разведки JustJoin.it API, после — удалены из venv (не нужен в production, источники работают через httpx).

Изменения 2026-08-03:
- Добавлен StartupJobs.cz (`sources/startupjobs.py`). Реверс показал: `www.startupjobs.cz/api/offers` — публичный JSON без авторизации, но параметры `keyword`/`limit` полностью игнорируются сервером (всегда возвращает один и тот же полный список ~410 активных вакансий, по 20/страницу, 21 страница). Категории `tester`/`qa-engineer` через `/api/areas` и `areas[]` фильтр тоже не работают на сервере. Решение: фетчим все страницы и фильтруем по `DEFAULT_KEYWORDS` внутри адаптера (через `core.filters.matches_keywords`) ДО обрезки по `limit`, иначе релевантные QA-вакансии могли не попасть в первые N результатов.
- Добавлен LinkedIn (`sources/linkedin.py`) — по запросу пользователя реализован пробный низкочастотный парсинг через публичный guest-эндпоинт `linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search` (без логина, без cookies). Работает через обычный httpx GET + regex по HTML-фрагментам (не JSON). Один запрос за опрос (10 результатов), keywords — булева OR-строка ("QA OR test automation OR QA lead OR QA architect OR SDET"), location жёстко "Prague, Czechia" (текст "Czech Republic" LinkedIn ошибочно геокодирует в Доминиканскую Республику — баг на их стороне, обнаружен эмпирически). Это серая зона ToS LinkedIn (см. hiQ Labs v. LinkedIn о легальности скрейпинга публичных данных — CFAA не нарушается, но контрактные претензии по ToS возможны); риск — блокировка IP VM при увеличении частоты/объёма запросов. Оставлено намеренно ограниченным по объёму согласно решению пользователя.

## Deploy

Задеплоено на Oracle Cloud Free Tier VM (2026-07-28): IP 158.180.20.184, user `ubuntu`, ключ `~/Downloads/keys/ssh-key-2026-07-28.key`, Ubuntu 24.04 (Python 3.12.3, venv в `/home/ubuntu/freelance_search/.venv`), systemd unit `freelance-bot.service` (enabled, автостарт). Инструкция: `.windsurf/workflows/deploy-oracle.md`.
Git-репозиторий: github.com/wolandgrin/work_search_bot (personal, email vladimir.grin@gmail.com настроен локально в репо).
Локальный процесс на Mac остановлен (во избежание дублей в Telegram) — теперь бот работает только на VM.
На той же VM уже был развёрнут другой бот ранее — при пересоздании инстанса (из-за несовпадения SSH-ключа) он был удалён, если не был отдельно забэкаплен пользователем.

## Notes

Проект стартовал 2026-07-27. См. `mcp_servers.md` для существующих MCP-инструментов.
