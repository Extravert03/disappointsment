from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import db

__all__ = (
    'reset_user_points_scheduler',
)

reset_user_points_scheduler = AsyncIOScheduler()
reset_user_points_scheduler.add_job(db.reset_user_points, CronTrigger(hour='*/3'))
