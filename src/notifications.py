import datetime
import logging
from dateutil import tz

from .config import TIMEZONE_TH
from .database import SessionLocal, Meeting, UserSettings
from .localization import STRINGS
from .utils import get_next_week_th
from .google_calendar import fetch_meetings_from_gcal
from .formatters import formatted_meeting

logger = logging.getLogger(__name__)

application = None
initialized = False
previous_map = {}

def initialize_notifications_variables(app):
    global application
    application = app
    logger.info("Notification variables initialized.")

def get_subscribed_users_for_new(meeting):
    session = SessionLocal()
    users = session.query(UserSettings).all()
    logger.debug(f"Found {len(users)} total users in settings")
    filtered = []
    for us in users:
        logger.debug(f"Checking user {us.user_id}: notify_new={us.notify_new}, filter_type={us.filter_type}, username={us.username}")
        if us.notify_new:
            if us.filter_type:
                if us.username and us.username in meeting["attendants"]:
                    filtered.append(us.user_id)
                    logger.debug(f"Added user {us.user_id} (matched attendant)")
            else:
                filtered.append(us.user_id)
                logger.debug(f"Added user {us.user_id} (no filter)")
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
    logger.debug(f"Subscribed users for meeting {meeting['id']} before {delta_minutes} minutes: {filtered}")
    return filtered

async def async_notify_new_meeting(meeting, user_list):
    text = STRINGS["notify_new_meeting"].format(details=formatted_meeting(meeting))
    for user_id in user_list:
        await application.bot.send_message(chat_id=user_id, text=text)
        logger.info(f"Sent new meeting notification to user {user_id} for meeting {meeting['id']}")

async def async_notify_before_meeting(meeting, user_list):
    text = STRINGS["notify_before_meeting"].format(details=formatted_meeting(meeting))
    for user_id in user_list:
        await application.bot.send_message(chat_id=user_id, text=text)
        logger.info(f"Sent before meeting notification to user {user_id} for meeting {meeting['id']}")

async def send_new_updated_notifications(new_meetings, updated_meetings):
    for meeting in new_meetings + updated_meetings:
        subs = get_subscribed_users_for_new(meeting)
        if subs:
            await async_notify_new_meeting(meeting, subs)
            logger.info(f"Sent notifications for new/updated meeting {meeting['id']}")

def meetings_differ(old_meeting, new_meeting):
    """Compare two meetings to detect meaningful changes."""
    if not old_meeting:
        return True
    
    fields_to_compare = [
        ('title', 'title'),
        ('start_th', 'start_th'),
        ('end_th', 'end_th'),
        ('attendants', 'attendants'),
        ('location', 'location'),
        ('hangoutLink', 'hangoutLink'),
        ('description', 'description')
    ]
    
    for db_field, dict_field in fields_to_compare:
        old_value = getattr(old_meeting, db_field) if isinstance(old_meeting, Meeting) else old_meeting[db_field]
        new_value = new_meeting[dict_field]
        
        if db_field == 'attendants':
            old_set = set(old_value.split(',')) if isinstance(old_value, str) else set(old_value)
            new_set = set(new_value)
            if old_set != new_set:
                return True
        elif old_value != new_value:
            return True
    return False

async def refresh_meetings(initial_run=False):
    """
    Refresh meetings from the start of today to the end of next week.
    """
    logger.info("Starting refresh_meetings")
    start_of_today = datetime.datetime.now(tz.gettz(TIMEZONE_TH)).replace(hour=0, minute=0, second=0, microsecond=0)
    nw_start, nw_end = get_next_week_th()
    start = start_of_today
    end = nw_end

    logger.info(f"Fetching meetings from {start} to {end}")
    new_meetings = fetch_meetings_from_gcal(start, end)
    logger.debug(f"Fetched {len(new_meetings)} meetings from Google Calendar")
    new_map = {m["id"]: m for m in new_meetings}

    session = SessionLocal()
    prev_meetings = session.query(Meeting).all()
    logger.debug(f"Found {len(prev_meetings)} existing meetings in database")
    prev_map = {m.id: m for m in prev_meetings}

    new_meetings_list = []
    updated_meetings = []
    
    # Check for new and updated meetings
    for mid, new_meeting in new_map.items():
        prev_meeting = prev_map.get(mid)
        if not prev_meeting:
            logger.info(f"New meeting found: {new_meeting['title']} ({mid})")
            new_meetings_list.append(new_meeting)
        elif meetings_differ(prev_meeting, new_meeting):
            logger.info(f"Updated meeting found: {new_meeting['title']} ({mid})")
            logger.debug(f"Changes in meeting {mid}: prev={prev_meeting}, new={new_meeting}")
            updated_meetings.append(new_meeting)

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
            attendants=",".join(m["attendants"]) if m["attendants"] else "",
            hangoutLink=m.get("hangoutLink", ""),
            location=m.get("location", ""),
            description=m.get("description", ""),
            updated=m["updated"],
        )
        session.add(meeting)
    session.commit()
    
    if not initial_run and (new_meetings_list or updated_meetings):
        logger.info(f"Sending notifications for {len(new_meetings_list)} new and {len(updated_meetings)} updated meetings")
        await send_new_updated_notifications(new_meetings_list, updated_meetings)
    
    session.close()
    logger.info("Refresh meetings completed")

async def notification_job(_context):
    """
    Check meetings starting soon and send notifications.
    """
    now = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    logger.debug(f"Running notification job at {now}")
    
    session = SessionLocal()
    meetings = session.query(Meeting).all()
    session.close()

    for m in meetings:
        start = m.start_th
        if start.tzinfo is None:
            start = start.replace(tzinfo=tz.gettz(TIMEZONE_TH))
        
        diff = (start - now).total_seconds() / 60.0
        
        # Check notifications windows with some tolerance
        notification_windows = [(60, 3), (15, 2), (5, 1)]  # (minutes, tolerance)
        
        for window, tolerance in notification_windows:
            if abs(diff - window) <= tolerance:
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
                user_list = get_subscribed_users_for_before(meeting, window)
                if user_list:
                    logger.info(f"Sending notifications for meeting {m.id} starting in {diff:.1f} minutes to {len(user_list)} users")
                    await async_notify_before_meeting(meeting, user_list)
