# freelance_search

Агрегатор вакансий/фриланс-проектов (QA, test automation, quality engineering) с уведомлениями в Telegram и MCP-сервером для поиска по запросу.

## Источники

| Источник | Тип | Комментарий |
|---|---|---|
| Remotive | API | remote-вакансии |
| RemoteOK | API | remote-вакансии, фильтр на клиенте |
| WeWorkRemotely | RSS | remote-вакансии |
| FL.ru | scraping | фриланс-проекты (`flru-parser`) |
| Guru | scraping | фриланс-проекты |
| FreelanceHunt | API | ~10 последних проектов без токена |
| Jobs.cz | scraping | постоянные вакансии в Чехии (QA Engineer/Lead/Test Lead/Architect/SDET) |
| NoFluffJobs | API | постоянные вакансии, category=testing, Poland-heavy, дедуп по `reference` |
| JustJoin.it | scraping (SSR HTML) | постоянные вакансии, category=testing, без авторизации |

Отключён: Kwork (`sources/kwork.py`, не зарегистрирован в `core/aggregator.py`) — требует российский паспорт для регистрации, недоступен пользователю.

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Для разработки (линтеры/тесты):
```bash
pip install -r requirements-dev.txt
```

## Конфигурация

Создать `.env` в корне проекта (не коммитится, см. `.gitignore`):

```env
TELEGRAM_BOT_TOKEN=<токен бота из @BotFather>
TELEGRAM_CHAT_ID=<chat_id, куда слать уведомления>
```

`TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID` обязательны для запуска бота.

## Запуск бота (Telegram-уведомления)

```bash
python -m bot.run_bot
```

Что происходит:
- каждые 15 минут (`bot/scheduler.py:POLL_INTERVAL_MINUTES`) опрашиваются все источники;
- вакансии фильтруются по ключевым словам (`core/filters.py:DEFAULT_KEYWORDS`);
- новые (не встречавшиеся ранее) вакансии отправляются в Telegram и запоминаются в `seen_jobs.db` (SQLite), чтобы не дублировать уведомления при следующих запусках.

## Запуск как MCP-сервер

```bash
python main.py
```

Предоставляет tool `search_freelance_jobs(query, sources, limit_per_source, keywords)` — можно вызывать из Cascade/Claude/другого MCP-клиента для разового поиска по произвольному запросу, без Telegram.

## Настройка фильтрации (ключевые слова)

`core/filters.py:DEFAULT_KEYWORDS` — список слов/фраз. Вакансия проходит фильтр, если:
- название (`title`) или теги содержат любое из ключевых слов (подстрокой, без учёта регистра), **или**
- описание содержит минимум 2 разных ключевых слова (`MIN_DESCRIPTION_MATCHES`).

Текущий набор покрывает QA Engineer/Lead/Architect (через `"qa"` как подстроку), Test Automation/Lead/Architect/Manager, SDET, Selenium/Playwright/Pytest, и русскоязычные "тестирование"/"тестировщик"/"автотест".

Чтобы добавить новую роль — допиши строку в список. Осторожно с короткими общими словами (например голое `"team lead"` или `"test"`) — они могут пропускать нерелевантные вакансии из других областей.

Для `jobs.cz` (`sources/jobscz.py:DEFAULT_QUERIES`) фильтрация происходит на уровне поисковых запросов к самому сайту — там свой список фраз для server-side поиска.

## Добавление нового источника

1. Создать `sources/<name>.py` с функцией `async def fetch_jobs(query: str, limit: int = 50) -> list[Job]`.
2. Зарегистрировать в `core/aggregator.py:SOURCE_ADAPTERS`.
3. `Job` модель — см. `sources/models.py` (обязательные поля: `source`, `title`, `url`).

## Проверки кода

```bash
./run_checks.sh
```

Запускает flake8, mypy, pylint (errors + similarities) и `pytest --collect-only`.

## Деплой на Oracle Cloud

См. `.windsurf/workflows/deploy-oracle.md` (workflow `/deploy-oracle`) — пошаговая инструкция для systemd-деплоя на always-free VM.
