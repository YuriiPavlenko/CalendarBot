import logging
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .google_calendar import fetch_meetings_from_gcal
from .utils import get_today_th, get_next_week_th
from .cache import cache
from .notifications import handle_new_and_updated_meetings, check_and_send_before_notifications
from .config import TIMEZONE_TH
from dateutil import tz
import asyncio

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def refresh_meetings():
    now_th = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    nw_start, nw_end = get_next_week_th()
    start = now_th
    end = nw_end
    new_meetings = fetch_meetings_from_gcal(start, end)
    await handle_new_and_updated_meetings({m["id"]:m for m in new_meetings})
    cache.update_meetings(new_meetings)

async def notification_job():
    meetings = cache.get_meetings()
    await check_and_send_before_notifications(meetings)

scheduler.add_job(refresh_meetings, 'interval', minutes=5)
scheduler.add_job(notification_job, 'interval', minutes=1)
