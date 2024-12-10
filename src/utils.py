import datetime
from src.config import TIMEZONE_TH
from dateutil import tz
from src.localization import STRINGS

def filter_meetings(meetings, filter_type, user_nickname):
    if filter_type == "mine":
        return [m for m in meetings if user_nickname in m["attendants"]]
    return meetings

def format_meeting(m):
    desc = m["description"] if m["description"] else ""
    loc = m["location"] if m["location"] else ""
    link = m["hangoutLink"] if m["hangoutLink"] else ""
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

def get_today_th():
    th_tz = tz.gettz(TIMEZONE_TH)
    now_th = datetime.datetime.now(th_tz)
    start_of_day = now_th.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + datetime.timedelta(days=1)
    return start_of_day, end_of_day

def get_tomorrow_th():
    th_tz = tz.gettz(TIMEZONE_TH)
    now_th = datetime.datetime.now(th_tz)
    start_of_tomorrow = (now_th + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_tomorrow = start_of_tomorrow + datetime.timedelta(days=1)
    return start_of_tomorrow, end_of_tomorrow

def get_rest_week_th():
    # rest of week until Saturday (not inclusive)
    th_tz = tz.gettz(TIMEZONE_TH)
    now_th = datetime.datetime.now(th_tz)
    today = now_th.date()
    # Find next Saturday
    # Monday=0, Tuesday=1, ... Sunday=6
    # We assume Monday-Friday are working days, Saturday=5
    weekday = today.weekday() # Monday=0
    # Need next Saturday: 
    # if weekday <=4 (Mon-Fri), end is Sat of this week
    # if weekday>4, no "rest of week"? 
    # Requirements: rest of week includes today until before next Saturday.
    # If today is Tuesday(1), we show Tue-Fri
    # If today is Saturday(5), rest of week presumably no working days left. Let's handle gracefully.
    days_until_saturday = 5 - weekday
    if days_until_saturday < 0:
        days_until_saturday = 0
    start_of_day = now_th.replace(hour=0,minute=0,second=0,microsecond=0)
    end_of_range = start_of_day + datetime.timedelta(days=days_until_saturday)
    return start_of_day, end_of_range

def get_next_week_th():
    # next week Monday-Friday
    th_tz = tz.gettz(TIMEZONE_TH)
    now_th = datetime.datetime.now(th_tz)
    today = now_th.date()
    weekday = today.weekday() 
    # Find next Monday (weekday=0)
    days_until_monday = (7 - weekday) % 7
    next_monday = now_th + datetime.timedelta(days=days_until_monday)
    # Monday to Friday next week
    start = next_monday.replace(hour=0,minute=0,second=0,microsecond=0)
    end = start + datetime.timedelta(days=5) # Mon +5days = Saturday midnight
    return start, end
