import datetime
from dateutil import tz
from localization import STRINGS
from config import TIMEZONE_TH, TIMEZONE_UA

def filter_meetings(meetings, filter_type, user_nickname):
    if filter_type == "mine":
        return [m for m in meetings if user_nickname in m["attendants"]]
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
    today = now_th.date()
    weekday = today.weekday()  # Monday=0
    days_until_saturday = 5 - weekday
    if days_until_saturday < 0:
        days_until_saturday = 0
    start_of_day = now_th.replace(hour=0,minute=0,second=0,microsecond=0)
    end_of_range = start_of_day + datetime.timedelta(days=days_until_saturday)
    return start_of_day, end_of_range

def get_next_week_th():
    th_tz = tz.gettz(TIMEZONE_TH)
    now_th = datetime.datetime.now(th_tz)
    today = now_th.date()
    weekday = today.weekday() 
    days_until_monday = (7 - weekday) % 7
    next_monday = now_th + datetime.timedelta(days=days_until_monday)
    start = next_monday.replace(hour=0,minute=0,second=0,microsecond=0)
    end = start + datetime.timedelta(days=5)
    return start, end

def format_meetings_list(meetings, period="today"):
    meetings = sorted(meetings, key=lambda m: m["start_th"])
    by_day = {}
    for m in meetings:
        day = m["start_th"].date()
        if day not in by_day:
            by_day[day] = []
        by_day[day].append(m)

    weekdays_ru = STRINGS["weekdays"]

    lines = []
    for day, day_meetings in by_day.items():
        date_str = day.strftime("%d.%m.%Y")
        if period == "today":
            header = STRINGS["meetings_for_today"].format(date=date_str)
        elif period == "tomorrow":
            header = STRINGS["meetings_for_tomorrow"].format(date=date_str)
        else:
            weekday_name = weekdays_ru[day.weekday()].upper()
            header = STRINGS["meetings_for_day_of_week"].format(weekday=weekday_name, date=date_str)

        lines.append(header)

        for mt in day_meetings:
            title = escape_markdown(mt["title"])
            start_ua = mt["start_ua"].strftime("%H:%M")
            end_ua = mt["end_ua"].strftime("%H:%M")
            start_th = mt["start_th"].strftime("%H:%M")
            end_th = mt["end_th"].strftime("%H:%M")

            lines.append(f"*{title}*")
            lines.append(STRINGS["ukraine_time"].format(start=start_ua, end=end_ua))
            lines.append(STRINGS["thailand_time"].format(start=start_th, end=end_th))

            if mt["location"]:
                loc = escape_markdown(mt["location"])
                lines.append(STRINGS["location_label"].format(location=loc))
            if mt["hangoutLink"]:
                link = escape_markdown(mt["hangoutLink"])
                lines.append(STRINGS["link_label"].format(link=link))
            if mt["description"]:
                desc = escape_markdown(mt["description"])
                lines.append(STRINGS["description_label"].format(description=desc))

            lines.append("")  # blank line after each meeting
        if lines[-1] == "":
            lines.pop()
        lines.append("")  # blank line after each day
    if lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines)


def escape_markdown(text: str) -> str:
    specials = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for s in specials:
        text = text.replace(s, f"\\{s}")
    return text
