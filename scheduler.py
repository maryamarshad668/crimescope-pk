from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
from pipeline import run_pipeline

scheduler = AsyncIOScheduler()

async def scheduled_run():
    print("⏰ Scheduled pipeline running...")
    await run_pipeline()

scheduler.add_job(
    scheduled_run,
    IntervalTrigger(hours=3),
    id="pipeline",
    name="Scrape every 3 hours",
    replace_existing=True
)

if __name__ == "__main__":
    scheduler.start()
    print("Scheduler started — pipeline runs every 3 hours")
    print("Press Ctrl+C to stop")
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        scheduler.shutdown()