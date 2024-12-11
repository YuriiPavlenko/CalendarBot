import logging
from .database import SessionLocal, get_user_settings
from .localization import STRINGS
from .utils import filter_meetings
import datetime
from .config import TIMEZONE_TH
from dateutil import tz
from sqlalchemy import text

logger = logging.getLogger(__name__)

application = None
initialized = False
previous_map = {}

def initialize_notifications_variables(app):
    global application
    application = app

def formatted_meeting(m):
    desc = m["description"] or ""
    loc = m["location"] or ""
    link = m["hangoutLink"] or ""
    attendants_str = ", ".join(m["attendants"]) if m["attendants"] else ""
    return STRINGS["meeting_details"].format(
        title=m["title"],
        start_ua=m["start_ua"].strftime("%Y-%m-%d %H:%M"),
        start_th=m["start_th"].strftime("%Y-%m-%d %H:%M"),
        end_ua=m["end_ua"].strftime("%Y-%m-%d %H:%M"),
        end_th=m["end_th"].strftime("%Y-%m-%d %H:%M"),
        attendants=attendants_str,
        location=loc,
        link=link,
        desc=desc
    )

def get_subscribed_users_for_new(meeting):
    session = SessionLocal()
    users = session.execute(text("SELECT user_id FROM user_settings")).fetchall()
    user_ids = [u[0] for u in users]
    filtered = []
    for uid in user_ids:
        us = get_user_settings(session, uid)
        user_identifier = us.username if us.username else f"@{uid}"
        if us.notify_new:
            if us.filter_type == "mine":
                if user_identifier in meeting["attendants"]:
                    filtered.append(uid)
            else:
                filtered.append(uid)
    session.close()
    return filtered

def get_subscribed_users_for_before(meeting, delta_minutes):
    session = SessionLocal()
    users = session.execute(text("SELECT user_id FROM user_settings")).fetchall()
    user_ids = [u[0] for u in users]
    filtered = []
    for uid in user_ids:
        us = get_user_settings(session, uid)
        user_identifier = us.username if us.username else f"@{uid}"
        notify_1h = us.notify_1h
        notify_15m = us.notify_15m
        notify_5m = us.notify_5m

        notify_attr = False
        if delta_minutes == 60 and notify_1h:
            notify_attr = True
        elif delta_minutes == 15 and notify_15m:
            notify_attr = True
        elif delta_minutes == 5 and notify_5m:
            notify_attr = True

        if notify_attr:
            if us.filter_type == "mine":
                if user_identifier in meeting["attendants"]:
                    filtered.append(uid)
            else:
                filtered.append(uid)
    session.close()
    return filtered

async def async_notify_new_meeting(meeting, user_list):
    text = STRINGS["notify_new_meeting"].format(details=formatted_meeting(meeting))
    for user_id in user_list:
        await application.bot.send_message(chat_id=user_id, text=text)

async def async_notify_before_meeting(meeting, user_list):
    text = STRINGS["notify_before_meeting"].format(details=formatted_meeting(meeting))
    for user_id in user_list:
        await application.bot.send_message(chat_id=user_id, text=text)

def handle_new_and_updated_meetings_sync(new_map):
    global initialized, previous_map
    if not initialized:
        previous_map = new_map
        initialized = True
        return [], []

    new_meetings = []
    updated_meetings = []
    for mid, m in new_map.items():
        if mid not in previous_map:
            new_meetings.append(m)
        else:
            if m["updated"] != previous_map[mid]["updated"]:
                updated_meetings.append(m)
    previous_map = new_map
    return new_meetings, updated_meetings

async def send_new_updated_notifications(new_meetings, updated_meetings):
    for nm in new_meetings:
        subs = get_subscribed_users_for_new(nm)
        if subs:
            await async_notify_new_meeting(nm, subs)
    for um in updated_meetings:
        subs = get_subscribed_users_for_new(um)
        if subs:
            await async_notify_new_meeting(um, subs)

async def refresh_meetings(initial_run=False):
    # from today to end of next week
    now_th = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    from utils import get_next_week_th
    nw_start, nw_end = get_next_week_th()
    start = now_th
    end = nw_end

    from google_calendar import fetch_meetings_from_gcal
    from cache import cache
    new_meetings = fetch_meetings_from_gcal(start, end)
    new_map = {m["id"]: m for m in new_meetings}
    new_meetings_list, updated_meetings = handle_new_and_updated_meetings_sync(new_map)
    cache.update_meetings(new_meetings)

    if not initial_run:
        # send notifications for new/updated
        await send_new_updated_notifications(new_meetings_list, updated_meetings)

async def notification_job(_context):
    # Check meetings starting soon
    from cache import cache
    meetings = cache.get_meetings()
    now = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    for m in meetings:
        start = m["start_th"]
        diff = (start - now).total_seconds() / 60.0
        diff_rounded = round(diff)
        if diff_rounded in [60,15,5]:
            user_list = get_subscribed_users_for_before(m, diff_rounded)
            if user_list:
                await async_notify_before_meeting(m, user_list)
