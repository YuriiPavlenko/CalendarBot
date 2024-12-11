import logging
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .google_calendar import fetch_meetings_from_gcal
from .utils import get_today_th
from .cache import cache
from .notifications import get_subscribed_users_for_new, notify_users_new_meeting
from .config import TIMEZONE_TH
from dateutil import tz

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def refresh_meetings():
    now = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    end = now + datetime.timedelta(days=7)
    new_meetings = fetch_meetings_from_gcal(now, end)
    old_meetings = cache.get_meetings()

    old_map = {m["id"]: m for m in old_meetings}
    new_map = {m["id"]: m for m in new_meetings}

    for mid, m in new_map.items():
        if mid not in old_map:
            # New meeting
            subscribers = get_subscribed_users_for_new(m)
            notify_users_new_meeting(m, subscribers)
        else:
            # Check if updated
            if m["updated"] != old_map[mid].get("updated"):
                # Updated meeting treated as new for notification
                subscribers = get_subscribed_users_for_new(m)
                notify_users_new_meeting(m, subscribers)

    cache.update_meetings(new_meetings)

scheduler.add_job(refresh_meetings, 'interval', minutes=5)
# Do not start the scheduler here; main.py will handle it.
