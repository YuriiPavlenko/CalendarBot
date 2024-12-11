import logging
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .google_calendar import fetch_meetings_from_gcal
from .utils import get_today_th, get_next_week_th
from .cache import cache
from .notifications import get_subscribed_users_for_new, notify_users_new_meeting
from .config import TIMEZONE_TH
from dateutil import tz

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def refresh_meetings():
    # Fetch meetings from today until end of next week
    start, _ = get_today_th()
    next_week_start, next_week_end = get_next_week_th()
    # We want all meetings until the end of next week:
    end = next_week_end

    new_meetings = fetch_meetings_from_gcal(start, end)
    old_meetings = cache.get_meetings()

    old_map = {m["id"]: m for m in old_meetings}
    new_map = {m["id"]: m for m in new_meetings}

    # Check for new or updated meetings
    for mid, m in new_map.items():
        if mid not in old_map:
            # New meeting
            subscribers = get_subscribed_users_for_new(m)
            notify_users_new_meeting(m, subscribers)
        else:
            # If updated timestamp changed
            if m["updated"] != old_map[mid].get("updated"):
                subscribers = get_subscribed_users_for_new(m)
                notify_users_new_meeting(m, subscribers)

    cache.update_meetings(new_meetings)
    logger.info("Meetings cache updated with latest data.")

# Refresh every 5 minutes
scheduler.add_job(refresh_meetings, 'interval', minutes=5)
