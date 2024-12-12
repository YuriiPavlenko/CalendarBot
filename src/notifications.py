import datetime
import logging
from dateutil import tz
from telegram import Bot
from .config import TIMEZONE_TH, TELEGRAM_BOT_TOKEN
from .database import SessionLocal, Meeting, UserSettings
from .localization import STRINGS
from .utils import get_next_week_th
from .google_calendar import fetch_meetings_from_gcal
from .formatters import formatted_meeting

logger = logging.getLogger(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def send_notification(user_id, meeting, is_new=False):
    text = STRINGS["notify_new_meeting" if is_new else "notify_before_meeting"].format(
        details=formatted_meeting(meeting)
    )
    await bot.send_message(chat_id=user_id, text=text)

async def refresh_meetings():
    """Simple meeting refresh: fetch new meetings and update database"""
    logger.info("Refreshing meetings")
    
    # Get time range
    now = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    _, end = get_next_week_th()
    
    # Fetch new meetings
    meetings = fetch_meetings_from_gcal(start, end)
    
    session = SessionLocal()
    
    # Get all subscribers who want notifications about new meetings
    subscribers = session.query(UserSettings).filter(UserSettings.notify_new == True).all()
    
    # Get existing meetings from the database
    existing_meetings = {m.id: m for m in session.query(Meeting).all()}
    
    # Clear and update database
    session.query(Meeting).delete()
    for m in meetings:
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
        
        # Check if the meeting is new or has changed
        existing_meeting = existing_meetings.get(m["id"])
        if not existing_meeting:
            # Notify subscribers about new meeting
            for user in subscribers:
                if not user.filter_type or (user.username and user.username in m["attendants"]):
                    await send_notification(user.user_id, m, is_new=True)
        elif (
            existing_meeting.title != m["title"] or
            existing_meeting.start_ua != m["start_ua"] or
            existing_meeting.end_ua != m["end_ua"] or
            existing_meeting.start_th != m["start_th"] or
            existing_meeting.end_th != m["end_th"] or
            existing_meeting.attendants != ",".join(m["attendants"]) or
            existing_meeting.hangoutLink != m.get("hangoutLink", "") or
            existing_meeting.location != m.get("location", "") or
            existing_meeting.description != m.get("description", "")
        ):
            # Notify subscribers about updated meeting
            for user in subscribers:
                if not user.filter_type or (user.username and user.username in m["attendants"]):
                    await send_notification(user.user_id, m, is_new=True)
    
    session.commit()
    session.close()

async def notification_job(_context):
    """Simple notification check: notify users about upcoming meetings"""
    now = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    
    session = SessionLocal()
    meetings = session.query(Meeting).all()
    users = session.query(UserSettings).all()
    
    for meeting in meetings:
        start = meeting.start_th
        if start.tzinfo is None:
            start = start.replace(tzinfo=tz.gettz(TIMEZONE_TH))
        
        minutes_until = (start - now).total_seconds() / 60.0
        
        # Check each notification window
        for minutes in [60, 15, 5]:
            if abs(minutes_until - minutes) <= 1:  # 1 minute tolerance
                for user in users:
                    should_notify = (
                        (minutes == 60 and user.notify_1h) or
                        (minutes == 15 and user.notify_15m) or
                        (minutes == 5 and user.notify_5m)
                    )
                    
                    if should_notify:
                        if not user.filter_type or (
                            user.username and 
                            user.username in (meeting.attendants.split(",") if meeting.attendants else [])
                        ):
                            await send_notification(user.user_id, {
                                "id": meeting.id,
                                "title": meeting.title,
                                "start_th": meeting.start_th,
                                "end_th": meeting.end_th,
                                "attendants": meeting.attendants.split(",") if meeting.attendants else [],
                                "hangoutLink": meeting.hangoutLink,
                                "location": meeting.location,
                                "description": meeting.description,
                            })
    
    session.close()
