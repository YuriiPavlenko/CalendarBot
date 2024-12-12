from dateutil import tz
from .config import TIMEZONE_TH
from datetime import datetime, timedelta

def filter_meetings(meetings, filter_type, user_identifier):
    # user_identifier = "@username" if user has username, else "@{user_id}"
    if filter_type:
        return [m for m in meetings if user_identifier in m["attendants"]]
    return meetings

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
    th_tz = tz.gettz(TIMEZONE_TH)
    now_th = datetime.now(th_tz)
    
    # Get start of today
    start_of_day = now_th.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate end of current week (Friday)
    weekday = now_th.weekday()  # 0 is Monday, 4 is Friday
    days_until_friday = 4 - weekday  # How many days until Friday
    
    if days_until_friday < 0:  # If it's already weekend
        end_of_range = start_of_day  # Just return today as end
    else:
        # Get end of Friday
        end_of_range = (start_of_day + timedelta(days=days_until_friday)).replace(
            hour=23, minute=59, second=59
        )
    
    return start_of_day, end_of_range

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
    if end_utc.tzinfo is None:
        end_utc = end_utc.replace(tzinfo=tz.UTC)
        
    return {
        "id": meeting.id,
        "title": meeting.title,
        "start_ua": start_utc.astimezone(tz.gettz(ua_tz)),
        "end_ua": end_utc.astimezone(tz.gettz(ua_tz)),
        "start_th": start_utc.astimezone(tz.gettz(th_tz)),
        "end_th": end_utc.astimezone(tz.gettz(th_tz)),
        "attendants": meeting.attendants.split(",") if meeting.attendants else [],
        "hangoutLink": meeting.hangoutLink,
        "location": meeting.location,
        "description": meeting.description,
    }
