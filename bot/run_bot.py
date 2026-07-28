import asyncio
import logging

from bot.scheduler import build_scheduler

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    scheduler = build_scheduler()
    scheduler.start()
    stop_event = asyncio.Event()
    await stop_event.wait()


if __name__ == "__main__":
    asyncio.run(main())
