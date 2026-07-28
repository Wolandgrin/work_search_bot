import logging

from telegram import Bot
from telegram.constants import ParseMode

from sources.models import Job

logger = logging.getLogger(__name__)


def format_job(job: Job) -> str:
    budget = ""
    if job.budget_min or job.budget_max:
        parts = [str(v) for v in (job.budget_min, job.budget_max) if v]
        budget_line = f"Budget: {'-'.join(parts)} {job.currency or ''}".strip()
        budget = f"\n{budget_line}"
    location = f"\nLocation: {job.location}" if job.location else ""
    return f"<b>{job.title}</b>\nSource: {job.source}{location}{budget}\n{job.url}"


class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.bot = Bot(token=token)
        self.chat_id = chat_id

    async def send_jobs(self, jobs: list[Job]) -> None:
        for job in jobs:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=format_job(job),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )
            logger.info("Sent job to Telegram: %s", job.title)
