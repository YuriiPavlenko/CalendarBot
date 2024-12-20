import logging
from dateutil import tz
from .config import TIMEZONE_TH
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def filter_meetings(meetings, filter_type, user_identifier):
    # user_identifier = "@username" if user has username, else "@{user_id}"
    if not filter_type:
        for meeting in meetings:
            if "attendants" not in meeting:
                meeting["attendants"] = []
        return meetings
    
    if meetings is None:
        return []
        
    filtered_meetings = []
    for meeting in meetings:
        attendants = meeting.get("attendants")
        if attendants is None:
            continue
        if isinstance(attendants, list):
            cleaned_attendants = [attendant.strip() for attendant in attendants if isinstance(attendant, str)]
            if user_identifier in cleaned_attendants:
                filtered_meetings.append(meeting)
        elif isinstance(attendants, str):
            cleaned_attendants = [attendant.strip() for attendant in attendants.split(",") if isinstance(attendant, str) and attendant.strip()]
            if user_identifier in cleaned_attendants:
                filtered_meetings.append(meeting)
    
    return filtered_meetings

def get_today_th():
    th_tz = tz.gettz(TIMEZONE_TH)
    now_th = datetime.now(th_tz)
    start_of_day = now_th.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    return start_of_day, end_of_day

def get_tomorrow_th():
    th_tz = tz.gettz(TIMEZONE_TH)
    now_th = datetime.now(th_tz)
    start_of_tomorrow = (now_th + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_tomorrow = start_of_tomorrow + timedelta(days=1)
    return start_of_tomorrow, end_of_tomorrow

def get_rest_week_th():
    """Get range from today until end of current week (Friday), including today."""
    th_tz = tz.gettz(TIMEZONE_TH)
    now_th = datetime.now(th_tz)
    weekday = now_th.weekday()  # 0-6, Monday is 0
    
    # Start from beginning of today
    start = now_th.replace(hour=0, minute=0, second=0, microsecond=0)
    
    if weekday > 4:  # If it's weekend (Saturday or Sunday)
        # Just return a one-day range for today
        end = start + timedelta(days=1)
    elif weekday == 4:  # If it's Friday
        # Just return today's range
        end = start + timedelta(days=1)
    else:
        # Find this week's Friday
        days_to_friday = 4 - weekday
        end = (start + timedelta(days=days_to_friday + 1))
    
    logger.info(f"Rest of week range: start={start.strftime('%Y-%m-%d %H:%M %Z')}, end={end.strftime('%Y-%m-%d %H:%M %Z')}, weekday={weekday}")
    return start, end

def get_next_week_th():
    th_tz = tz.gettz(TIMEZONE_TH)
    now_th = datetime.now(th_tz)
    weekday = now_th.weekday()
    days_until_monday = (7 - weekday) % 7
    next_monday = now_th + timedelta(days=days_until_monday)
    start = next_monday.replace(hour=0,minute=0,second=0,microsecond=0)
    end = start + timedelta(days=5)
    return start, end

def get_end_of_next_week():
    now = datetime.now()
    days_ahead = 11 - now.weekday()  # Next week's Friday
    if days_ahead <= 0:
        days_ahead += 7
    next_friday = now + timedelta(days_ahead)
    end_of_next_week = next_friday.replace(hour=23, minute=59, second=59, microsecond=0)
    return end_of_next_week

def convert_meeting_to_display(meeting, ua_tz='Europe/Kiev', th_tz='Asia/Bangkok'):
    """Convert database meeting (UTC) to display format with UA and TH times."""
    if not meeting:
        return None
        
    start_utc = meeting.start_time
    end_utc = meeting.end_time
    
    if start_utc.tzinfo is None:
        start_utc = start_utc.replace(tzinfo=tz.UTC)
    if end_utc is not None and end_utc.tzinfo is None:
        end_utc = end_utc.replace(tzinfo=tz.UTC)
        
    return {
        "id": meeting.id,
        "title": meeting.title,
        "start_ua": start_utc.astimezone(tz.gettz(ua_tz)),
        "end_ua": end_utc.astimezone(tz.gettz(ua_tz)) if end_utc else None,
        "start_th": start_utc.astimezone(tz.gettz(th_tz)),
        "end_th": end_utc.astimezone(tz.gettz(th_tz)) if end_utc else None,
        "attendants": meeting.attendants.split(",") if meeting.attendants else [],
        "hangoutLink": meeting.hangoutLink,
        "location": meeting.location,
        "description": meeting.description,
    }
