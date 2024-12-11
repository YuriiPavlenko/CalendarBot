import logging
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .google_calendar import fetch_meetings_from_gcal
from .utils import get_today_th, get_next_week_th
from .cache import cache
from .notifications import get_subscribed_users_for_new, notify_users_new_meeting, check_and_send_before_notifications
from .config import TIMEZONE_TH
from dateutil import tz

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def refresh_meetings():
    # Fetch from today to end of next week
    now_th = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    start = now_th
    nw_start, nw_end = get_next_week_th()

    # We want from today to end of next week
    # next_week_th gives Mon-Fri of next week, if you want full next week (Mon-Fri)
    # If you want a full extended range: today -> end of next week (Friday)
    # It's already what get_next_week_th does: next week's Mon-Fri
    # So end = nw_end

    end = nw_end
    new_meetings = fetch_meetings_from_gcal(start, end)
    old_meetings = cache.get_meetings()

    old_map = {m["id"]: m for m in old_meetings}
    new_map = {m["id"]: m for m in new_meetings}

    # Check new or updated
    for mid, m in new_map.items():
        if mid not in old_map:
            # New meeting
            subscribers = get_subscribed_users_for_new(m)
            if subscribers:
                notify_users_new_meeting(m, subscribers)
        else:
            # Check if updated
            if m["updated"] != old_map[mid].get("updated"):
                # Updated meeting treat like new
                subscribers = get_subscribed_users_for_new(m)
                if subscribers:
                    notify_users_new_meeting(m, subscribers)

    cache.update_meetings(new_meetings)

def notification_job():
    # Runs every minute
    meetings = cache.get_meetings()
    check_and_send_before_notifications(meetings)

scheduler.add_job(refresh_meetings, 'interval', minutes=5)
scheduler.add_job(notification_job, 'interval', minutes=1)
