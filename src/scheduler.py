import logging
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .google_calendar import fetch_meetings_from_gcal
from .utils import get_today_th, get_next_week_th
from .cache import cache
from .notifications import handle_new_and_updated_meetings, check_and_send_before_notifications
from .config import TIMEZONE_TH
from dateutil import tz

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()

def refresh_meetings():
    now_th = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    # from today to end of next week
    nw_start, nw_end = get_next_week_th()
    start = now_th
    end = nw_end
    new_meetings = fetch_meetings_from_gcal(start, end)
    handle_new_and_updated_meetings({m["id"]: m for m in new_meetings})
    cache.update_meetings(new_meetings)

def notification_job():
    meetings = cache.get_meetings()
    check_and_send_before_notifications(meetings)

scheduler.add_job(refresh_meetings, 'interval', minutes=5)
scheduler.add_job(notification_job, 'interval', minutes=1)
