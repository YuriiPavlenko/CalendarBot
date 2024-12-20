import datetime
import logging
from dateutil import tz
from telegram import Bot
from .config import TIMEZONE_TH, TELEGRAM_BOT_TOKEN  # Add relative import
from database import SessionLocal, Meeting, UserSettings
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
    if isinstance(meeting, dict):
        return meeting.get(field, default)
    return getattr(meeting, field, default)

def normalize_datetime(dt):
    """Normalize datetime to UTC."""
    if dt is None:
        return None
    if not isinstance(dt, datetime.datetime):
        return dt
    
    # If datetime has timezone info, convert to UTC
    if dt.tzinfo is not None:
        return dt.astimezone(tz.UTC)
    # If no timezone, assume UTC
    return dt.replace(tzinfo=tz.UTC)

def compare_datetimes(dt1, dt2):
    """Compare two datetimes in UTC."""
    norm1 = normalize_datetime(dt1)
    norm2 = normalize_datetime(dt2)
    return norm1 == norm2

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
    """Refresh meetings from Google Calendar."""
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
        # Get subscribers but don't return if empty
        subscribers = session.query(UserSettings).filter(UserSettings.notify_new == True).all()
        if subscribers:
            logger.debug(f"Found {len(subscribers)} subscribers for new meeting notifications")
        else:
            logger.info("No subscribers found for notifications")
        
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
                # Only notify if there are subscribers
                if subscribers:
                    for user in subscribers:
                        if user and user.user_id and (
                            not user.filter_by_attendant or 
                            (user.username and user.username in (m.get("attendants", []) or []))
                        ):
                            logger.debug(f"Notifying user {user.user_id} about new meeting {m['id']}")
                            await send_notification(user.user_id, m, is_new=True)
            else:
                # Move comparison block inside the else clause
                title_old = existing_meeting.title or ""
                title_new = m.get("title") or ""
                if title_old != title_new:
                    logger.debug(f"Title changed: '{title_old}' -> '{title_new}'")

                attendants_old = existing_meeting.attendants or ""
                attendants_new = ",".join(m.get("attendants", []) or [])
                if attendants_old != attendants_new:
                    logger.debug(f"Attendants changed: '{attendants_old}' -> '{attendants_new}'")

                hangout_old = existing_meeting.hangoutLink or ""
                hangout_new = m.get("hangoutLink") or ""
                if hangout_old != hangout_new:
                    logger.debug(f"Hangout link changed: '{hangout_old}' -> '{hangout_new}'")

                location_old = existing_meeting.location or ""
                location_new = m.get("location") or ""
                if location_old != location_new:
                    logger.debug(f"Location changed: '{location_old}' -> '{location_new}'")

                desc_old = existing_meeting.description or ""
                desc_new = m.get("description") or ""
                if desc_old != desc_new:
                    logger.debug(f"Description changed: '{desc_old}' -> '{desc_new}'")

                if (
                    title_old != title_new or
                    not compare_datetimes(existing_meeting.start_time, m.get("start_ua")) or
                    not compare_datetimes(existing_meeting.end_time, m.get("end_ua")) or
                    attendants_old != attendants_new or
                    hangout_old != hangout_new or
                    location_old != location_new or
                    desc_old != desc_new
                ):
                    updated_count += 1
                    logger.debug(f"Updated meeting found: {m['title']} ({m['id']})")
                    if subscribers:
                        for user in subscribers:
                            if user and user.user_id and (
                                not user.filter_by_attendant or 
                                (user.username and user.username in (m.get("attendants", []) or []))
                            ):
                                logger.debug(f"Notifying user {user.user_id} about updated meeting {m['id']}")
                                await send_notification(user.user_id, m, is_new=True)
        
        # Update database regardless of subscribers
        session.query(Meeting).delete()
        logger.debug("Cleared existing meetings from database")
        
        for m in meetings:
            if not m or not m.get("id"):
                continue
                
            meeting = Meeting(
                id=m.get("id"),
                title=m.get("title", "Untitled"),
                # Store everything in UTC
                start_time=normalize_datetime(m.get("start_ua")),
                end_time=normalize_datetime(m.get("end_ua")),
                attendants=",".join(m.get("attendants", []) or []),
                hangoutLink=m.get("hangoutLink", ""),
                location=m.get("location", ""),
                description=m.get("description", ""),
                updated=m.get("updated"),
            )
            
            if not meeting.start_time or not meeting.end_time:
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
    now = datetime.datetime.now(tz.UTC)
    
    session = SessionLocal()
    try:
        meetings = session.query(Meeting).all() or []
        users = session.query(UserSettings).all() or []
        logger.debug(f"Processing {len(meetings)} meetings for {len(users)} users")
        
        notifications_sent = 0
        for meeting in meetings:
            if not meeting or not meeting.start_time:
                logger.warning(f"Skipping invalid meeting: {getattr(meeting, 'id', 'unknown')}")
                continue
                
            start = normalize_datetime(meeting.start_time)
            
            minutes_until = (start - now).total_seconds() / 60.0
            logger.debug(f"Meeting {meeting.id} starts in {minutes_until:.1f} minutes")
            
            # Define notification windows with wider tolerances
            notification_windows = [
                (60, 1.0, "1-hour"),     # 60 minutes ± 2 minutes
                (15, 1.0, "15-minute"),   # 15 minutes ± 1 minute
                (5, 1.0, "5-minute")      # 5 minutes ± 30 seconds
            ]
            
            for target_minutes, tolerance, window_name in notification_windows:
                window_min = target_minutes - tolerance
                window_max = target_minutes + tolerance
                in_window = window_min <= minutes_until <= window_max
                
                logger.debug(
                    f"Checking {window_name} window for meeting {meeting.id}: "
                    f"window={window_min:.1f}-{window_max:.1f}, "
                    f"minutes_until={minutes_until:.1f}, matches={in_window}"
                )
                
                if in_window:
                    for user in users:
                        if not user or not user.user_id:
                            continue
                            
                        should_notify = (
                            (target_minutes == 60 and user.notify_1h) or
                            (target_minutes == 15 and user.notify_15m) or
                            (target_minutes == 5 and user.notify_5m)
                        )
                        
                        if should_notify:
                            attendants = (meeting.attendants or "").split(",") if meeting.attendants else []
                            if not user.filter_by_attendant or (
                                user.username and 
                                user.username in attendants
                            ):
                                logger.debug(f"Sending {window_name} notification to user {user.user_id}")
                                # Convert meeting to dict format with proper timezone info
                                meeting_dict = {
                                    "id": meeting.id,
                                    "title": meeting.title or "Untitled",
                                    "start_time": meeting.start_time,  # Let formatter handle conversion
                                    "end_time": meeting.end_time,      # Let formatter handle conversion
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
