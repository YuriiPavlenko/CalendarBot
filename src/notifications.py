import datetime
from dateutil import tz

from .config import TIMEZONE_TH
from .database import SessionLocal, Meeting, UserSettings
from .localization import STRINGS
from .utils import get_next_week_th
from .google_calendar import fetch_meetings_from_gcal
from .formatters import formatted_meeting

application = None
initialized = False
previous_map = {}

def initialize_notifications_variables(app):
    global application
    application = app

# Removed formatted_meeting function

def get_subscribed_users_for_new(meeting):
    session = SessionLocal()
    users = session.query(UserSettings).all()
    filtered = []
    for us in users:
        if us.notify_new:
            if us.filter_type:
                if us.username and us.username in meeting["attendants"]:
                    filtered.append(us.user_id)
            else:
                filtered.append(us.user_id)
    session.close()
    return filtered

def get_subscribed_users_for_before(meeting, delta_minutes):
    session = SessionLocal()
    users = session.query(UserSettings).all()
    filtered = []
    for us in users:
        notify_attr = (
            (delta_minutes == 60 and us.notify_1h) or
            (delta_minutes == 15 and us.notify_15m) or
            (delta_minutes == 5 and us.notify_5m)
        )
        if notify_attr:
            if us.filter_type:
                if us.username and us.username in meeting["attendants"]:
                    filtered.append(us.user_id)
            else:
                filtered.append(us.user_id)
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

async def send_new_updated_notifications(new_meetings, updated_meetings):
    for meeting in new_meetings + updated_meetings:
        subs = get_subscribed_users_for_new(meeting)
        if subs:
            await async_notify_new_meeting(meeting, subs)

async def refresh_meetings(initial_run=False):
    """
    Refresh meetings from the start of today to the end of next week.
    """
    start_of_today = datetime.datetime.now(tz.gettz(TIMEZONE_TH)).replace(hour=0, minute=0, second=0, microsecond=0)
    nw_start, nw_end = get_next_week_th()
    start = start_of_today
    end = nw_end

    new_meetings = fetch_meetings_from_gcal(start, end)
    new_map = {m["id"]: m for m in new_meetings}

    session = SessionLocal()
    prev_meetings = session.query(Meeting).all()
    prev_map = {m.id: m.updated for m in prev_meetings}

    new_meetings_list = []
    updated_meetings = []
    for mid, m in new_map.items():
        if mid not in prev_map:
            new_meetings_list.append(m)
        elif m["updated"] != prev_map[mid]:
            updated_meetings.append(m)

    # Delete old meetings
    session.query(Meeting).delete()
    # Add new meetings
    for m in new_meetings:
        meeting = Meeting(
            id=m["id"],
            title=m["title"],
            start_ua=m["start_ua"],
            end_ua=m["end_ua"],
            start_th=m["start_th"],
            end_th=m["end_th"],
            attendants=",".join(m["attendants"]),
            hangoutLink=m.get("hangoutLink"),
            location=m.get("location"),
            description=m.get("description"),
            updated=m["updated"],
        )
        session.add(meeting)
    session.commit()
    if not initial_run:
        await send_new_updated_notifications(new_meetings_list, updated_meetings)
    session.close()

async def notification_job(_context):
    """
    Check meetings starting soon and send notifications.
    """
    now = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    session = SessionLocal()
    meetings = session.query(Meeting).all()
    session.close()

    for m in meetings:
        start = m.start_th
        diff = (start - now).total_seconds() / 60.0
        diff_rounded = round(diff)
        if diff_rounded in [60, 15, 5]:
            meeting = {
                "id": m.id,
                "title": m.title,
                "start_ua": m.start_ua,
                "end_ua": m.end_ua,
                "start_th": m.start_th,
                "end_th": m.end_th,
                "attendants": m.attendants.split(",") if m.attendants else [],
                "hangoutLink": m.hangoutLink,
                "location": m.location,
                "description": m.description,
                "updated": m.updated,
            }
            user_list = get_subscribed_users_for_before(meeting, diff_rounded)
            if user_list:
                await async_notify_before_meeting(meeting, user_list)
