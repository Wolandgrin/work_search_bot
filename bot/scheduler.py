import logging
import os
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv

from bot.notifier import TelegramNotifier
from core.aggregator import search_jobs
from core.filters import DEFAULT_KEYWORDS
from core.storage import SeenJobsStore

load_dotenv()

logger = logging.getLogger(__name__)

POLL_INTERVAL_MINUTES = 15
SEARCH_QUERY = ""
LIMIT_PER_SOURCE = 100


async def poll_and_notify(notifier: TelegramNotifier, store: SeenJobsStore) -> None:
    jobs = await search_jobs(
        query=SEARCH_QUERY,
        limit_per_source=LIMIT_PER_SOURCE,
        keywords=DEFAULT_KEYWORDS,
    )
    keys = [job.dedup_key() for job in jobs]
    new_keys = set(store.filter_new(keys))
    new_jobs = [job for job in jobs if job.dedup_key() in new_keys]
    if new_jobs:
        await notifier.send_jobs(new_jobs)
        store.mark_seen([job.dedup_key() for job in new_jobs])
    logger.info("Poll complete: %d new jobs out of %d total", len(new_jobs), len(jobs))


def build_scheduler() -> AsyncIOScheduler:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    notifier = TelegramNotifier(token=token, chat_id=chat_id)
    store = SeenJobsStore()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        poll_and_notify,
        "interval",
        minutes=POLL_INTERVAL_MINUTES,
        args=[notifier, store],
        next_run_time=datetime.now(),
    )
    return scheduler
