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

def safe_get_meeting_data(meeting, field, default=None):
    """Safely get meeting data with null checking."""
    if meeting is None:
        return default
    if isinstance(meeting, Meeting):
        return getattr(meeting, field, default)
    return meeting.get(field, default)

async def send_notification(user_id, meeting, is_new=False):
    if not user_id or not meeting:
        logger.error("Invalid user_id or meeting data")
        return
    
    meeting_id = safe_get_meeting_data(meeting, 'id', 'unknown')
    logger.debug(f"Sending {'new' if is_new else 'reminder'} notification to user {user_id} for meeting {meeting_id}")
    
    try:
        text = STRINGS["notify_new_meeting" if is_new else "notify_before_meeting"].format(
            details=formatted_meeting(meeting)
        )
        if not text:
            logger.error(f"Failed to format notification text for meeting {meeting_id}")
            return
            
        await bot.send_message(chat_id=user_id, text=text)
        logger.info(f"Successfully sent notification to user {user_id} for meeting {meeting_id}")
    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {str(e)}")

async def refresh_meetings(context=None):
    """Refresh meetings from Google Calendar.
    
    Args:
        context: telegram.ext.CallbackContext, optional - Required for job queue compatibility
    """
    logger.info("Starting meetings refresh")
    
    now = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    _, end = get_next_week_th()
    logger.info(f"Fetching meetings from {start} to {end}")
    
    try:
        meetings = fetch_meetings_from_gcal(start, end)
        if not meetings:
            logger.warning("No meetings returned from Google Calendar")
            return
        logger.info(f"Successfully fetched {len(meetings)} meetings from Google Calendar")
    except Exception as e:
        logger.error(f"Failed to fetch meetings: {str(e)}")
        return

    session = SessionLocal()
    try:
        subscribers = session.query(UserSettings).filter(UserSettings.notify_new == True).all()
        if not subscribers:
            logger.info("No subscribers found for notifications")
            return
            
        logger.debug(f"Found {len(subscribers)} subscribers for new meeting notifications")
        
        existing_meetings = {m.id: m for m in session.query(Meeting).all() if m and m.id}
        logger.debug(f"Found {len(existing_meetings)} existing meetings in database")
        
        new_count = 0
        updated_count = 0
        
        # First compare meetings without modifying the database
        for m in meetings:
            if not m or not m.get("id"):
                logger.warning("Skipping invalid meeting entry")
                continue
                
            existing_meeting = existing_meetings.get(m.get("id"))
            if not existing_meeting:
                new_count += 1
                logger.debug(f"New meeting found: {m.get('title', 'Untitled')} ({m.get('id')})")
                # Notify about truly new meetings
                for user in subscribers:
                    if user and user.user_id and (
                        not user.filter_by_attendant or 
                        (user.username and user.username in (m.get("attendants", []) or []))
                    ):
                        logger.debug(f"Notifying user {user.user_id} about new meeting {m['id']}")
                        await send_notification(user.user_id, m, is_new=True)
            elif (
                (existing_meeting.title or "") != (m.get("title") or "") or
                existing_meeting.start_ua != m.get("start_ua") or
                existing_meeting.end_ua != m.get("end_ua") or
                existing_meeting.start_th != m.get("start_th") or
                existing_meeting.end_th != m.get("end_th") or
                (existing_meeting.attendants or "") == ",".join(m.get("attendants", []) or []) or
                (existing_meeting.hangoutLink or "") != (m.get("hangoutLink") or "") or
                (existing_meeting.location or "") != (m.get("location") or "") or
                (existing_meeting.description or "") != (m.get("description") or "")
            ):
                updated_count += 1
                # Only notify about actually updated meetings
                logger.debug(f"Updated meeting found: {m['title']} ({m['id']})")
                for user in subscribers:
                    if user and user.user_id and (
                        not user.filter_by_attendant or 
                        (user.username and user.username in (m.get("attendants", []) or []))
                    ):
                        logger.debug(f"Notifying user {user.user_id} about updated meeting {m['id']}")
                        await send_notification(user.user_id, m, is_new=True)
        
        # Only after comparison, update the database
        session.query(Meeting).delete()
        logger.debug("Cleared existing meetings from database")
        
        for m in meetings:
            if not m or not m.get("id"):
                continue
                
            meeting = Meeting(
                id=m.get("id"),
                title=m.get("title", "Untitled"),
                start_ua=m.get("start_ua"),
                end_ua=m.get("end_ua"),
                start_th=m.get("start_th"),
                end_th=m.get("end_th"),
                attendants=",".join(m.get("attendants", []) or []),
                hangoutLink=m.get("hangoutLink", ""),
                location=m.get("location", ""),
                description=m.get("description", ""),
                updated=m.get("updated"),
            )
            
            if not meeting.start_th or not meeting.end_th:
                logger.warning(f"Skipping meeting {meeting.id} due to missing time data")
                continue
                
            session.add(meeting)
        
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
        meetings = session.query(Meeting).all() or []
        users = session.query(UserSettings).all() or []
        logger.debug(f"Processing {len(meetings)} meetings for {len(users)} users")
        
        notifications_sent = 0
        for meeting in meetings:
            if not meeting or not meeting.start_th:
                logger.warning(f"Skipping invalid meeting: {getattr(meeting, 'id', 'unknown')}")
                continue
                
            start = meeting.start_th
            if start.tzinfo is None:
                start = start.replace(tzinfo=tz.gettz(TIMEZONE_TH))
            
            minutes_until = (start - now).total_seconds() / 60.0
            logger.debug(f"Meeting {meeting.id} starts in {minutes_until:.1f} minutes")
            
            for minutes in [60, 15, 5]:
                if abs(minutes_until - minutes) <= 1:
                    logger.debug(f"Meeting {meeting.id} matches {minutes}-minute notification window")
                    for user in users:
                        if not user or not user.user_id:
                            continue
                            
                        should_notify = (
                            (minutes == 60 and user.notify_1h) or
                            (minutes == 15 and user.notify_15m) or
                            (minutes == 5 and user.notify_5m)
                        )
                        
                        if should_notify:
                            attendants = (meeting.attendants or "").split(",") if meeting.attendants else []
                            if not user.filter_by_attendant or (
                                user.username and 
                                user.username in attendants
                            ):
                                logger.debug(f"Sending {minutes}-minute notification to user {user.user_id}")
                                meeting_dict = {
                                    "id": meeting.id,
                                    "title": meeting.title or "Untitled",
                                    "start_th": meeting.start_th,
                                    "end_th": meeting.end_th,
                                    "attendants": attendants,
                                    "hangoutLink": meeting.hangoutLink or "",
                                    "location": meeting.location or "",
                                    "description": meeting.description or "",
                                }
                                await send_notification(user.user_id, meeting_dict)
                                notifications_sent += 1
        
        logger.info(f"Notification job complete. Sent {notifications_sent} notifications")
    except Exception as e:
        logger.error(f"Error during notification job: {str(e)}")
    finally:
        session.close()
