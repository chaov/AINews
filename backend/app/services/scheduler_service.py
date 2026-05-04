from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.config import settings
from app.agents.crawler_agent import run_crawler

scheduler = AsyncIOScheduler()


async def scheduled_crawl():
    try:
        result = await run_crawler()
        print(f"Scheduled crawl completed: {result}")
    except Exception as e:
        print(f"Scheduled crawl failed: {e}")


def start_scheduler():
    scheduler.add_job(
        scheduled_crawl,
        "interval",
        minutes=settings.CRAWLER_INTERVAL_MINUTES,
        id="crawl_news",
        replace_existing=True,
    )
    scheduler.start()
    print(f"Scheduler started with interval: {settings.CRAWLER_INTERVAL_MINUTES} minutes")
