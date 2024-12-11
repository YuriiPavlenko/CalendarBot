import datetime
from dateutil import tz
from .config import TIMEZONE_TH
from .localization import STRINGS

def filter_meetings(meetings, filter_type, user_identifier):
    # user_identifier = "@username" if user has username, else "@{user_id}"
    if filter_type == "mine":
        return [m for m in meetings if user_identifier in m["attendants"]]
    return meetings

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
    th_tz = tz.gettz(TIMEZONE_TH)
    now_th = datetime.datetime.now(th_tz)
    weekday = now_th.weekday()
    days_until_saturday = 5 - weekday
    if days_until_saturday < 0:
        days_until_saturday = 0
    start_of_day = now_th.replace(hour=0,minute=0,second=0,microsecond=0)
    end_of_range = start_of_day + datetime.timedelta(days=days_until_saturday)
    return start_of_day, end_of_range

def get_next_week_th():
    th_tz = tz.gettz(TIMEZONE_TH)
    now_th = datetime.datetime.now(th_tz)
    weekday = now_th.weekday()
    days_until_monday = (7 - weekday) % 7
    next_monday = now_th + datetime.timedelta(days=days_until_monday)
    start = next_monday.replace(hour=0,minute=0,second=0,microsecond=0)
    end = start + datetime.timedelta(days=5)
    return start, end
