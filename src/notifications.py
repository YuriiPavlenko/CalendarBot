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
    logger.debug(f"Sending {'new' if is_new else 'reminder'} notification to user {user_id} for meeting {meeting.get('id')}")
    text = STRINGS["notify_new_meeting" if is_new else "notify_before_meeting"].format(
        details=formatted_meeting(meeting)
    )
    try:
        await bot.send_message(chat_id=user_id, text=text)
        logger.info(f"Successfully sent notification to user {user_id} for meeting {meeting.get('id')}")
    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {str(e)}")

async def refresh_meetings():
    logger.info("Starting meetings refresh")
    
    now = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    _, end = get_next_week_th()
    logger.info(f"Fetching meetings from {start} to {end}")
    
    try:
        meetings = fetch_meetings_from_gcal(start, end)
        logger.info(f"Successfully fetched {meetings} meetings from Google Calendar")
    except Exception as e:
        logger.error(f"Failed to fetch meetings: {str(e)}")
        return

    session = SessionLocal()
    try:
        subscribers = session.query(UserSettings).filter(UserSettings.notify_new == True).all()
        logger.debug(f"Found {len(subscribers)} subscribers for new meeting notifications")
        
        existing_meetings = {m.id: m for m in session.query(Meeting).all()}
        logger.debug(f"Found {existing_meetings} existing meetings in database")
        
        session.query(Meeting).delete()
        logger.debug("Cleared existing meetings from database")
        
        new_count = 0
        updated_count = 0
        
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
            
            existing_meeting = existing_meetings.get(m["id"])
            if not existing_meeting:
                new_count += 1
                logger.debug(f"New meeting found: {m['title']} ({m['id']})")
                for user in subscribers:
                    if not user.filter_type or (user.username and user.username in m["attendants"]):
                        logger.debug(f"Notifying user {user.user_id} about new meeting {m['id']}")
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
                updated_count += 1
                logger.debug(f"Updated meeting found: {m['title']} ({m['id']})")
                for user in subscribers:
                    if not user.filter_type or (user.username and user.username in m["attendants"]):
                        logger.debug(f"Notifying user {user.user_id} about updated meeting {m['id']}")
                        await send_notification(user.user_id, m, is_new=True)
        
        session.commit()
        logger.info(f"Refresh complete. New meetings: {new_count}, Updated meetings: {updated_count}")
    except Exception as e:
        logger.error(f"Error during refresh: {str(e)}")
        session.rollback()
    finally:
        session.close()

async def notification_job(_context):
    logger.debug("Starting notification job")
    now = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    
    session = SessionLocal()
    try:
        meetings = session.query(Meeting).all()
        users = session.query(UserSettings).all()
        logger.debug(f"Processing {len(meetings)} meetings for {len(users)} users")
        
        notifications_sent = 0
        for meeting in meetings:
            start = meeting.start_th
            if start.tzinfo is None:
                start = start.replace(tzinfo=tz.gettz(TIMEZONE_TH))
            
            minutes_until = (start - now).total_seconds() / 60.0
            logger.debug(f"Meeting {meeting.id} starts in {minutes_until:.1f} minutes")
            
            for minutes in [60, 15, 5]:
                if abs(minutes_until - minutes) <= 1:
                    logger.debug(f"Meeting {meeting.id} matches {minutes}-minute notification window")
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
                                logger.debug(f"Sending {minutes}-minute notification to user {user.user_id}")
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
                                notifications_sent += 1
        
        logger.info(f"Notification job complete. Sent {notifications_sent} notifications")
    except Exception as e:
        logger.error(f"Error during notification job: {str(e)}")
    finally:
        session.close()
