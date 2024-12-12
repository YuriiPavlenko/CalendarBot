from dateutil import tz
from .config import TIMEZONE_TH
from .localization import STRINGS

def convert_to_timezone(dt, timezone):
    """Convert UTC datetime to target timezone."""
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz.UTC)
    return dt.astimezone(tz.gettz(timezone))

def format_meeting_time(meeting, user_timezone='Europe/Kiev'):
    """Format meeting times according to user's timezone."""
    start = convert_to_timezone(meeting.start_time, user_timezone)
    end = convert_to_timezone(meeting.end_time, user_timezone)
    
    # Format according to locale
    if user_timezone == TIMEZONE_TH:
        time_format = "%H:%M %d/%m/%Y"
    else:
        time_format = "%H:%M %d.%m.%Y"
    
    return f"{start.strftime(time_format)} - {end.strftime(time_format)}"

def format_meetings_list(meetings, period="today"):
    # unchanged
    th_tz = tz.gettz(TIMEZONE_TH)
    meetings = sorted(meetings, key=lambda m: m["start_th"])
    by_day = {}
    weekdays_ru = STRINGS["weekdays"]
    for m in meetings:
        day = m["start_th"].date()
        if day not in by_day:
            by_day[day] = []
        by_day[day].append(m)

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
        lines.append("")
        for mt in day_meetings:
            title = mt["title"]
            start_ua = mt["start_ua"].strftime("%H:%M")
            end_ua = mt["end_ua"].strftime("%H:%M")
            start_th = mt["start_th"].strftime("%H:%M")
            end_th = mt["end_th"].strftime("%H:%M")
            lines.append(f"{title}")
            lines.append(STRINGS["thailand_time"].format(start=start_th, end=end_th))
            lines.append(STRINGS["ukraine_time"].format(start=start_ua, end=end_ua))
            if mt["attendants"]:
                lines.append("Участники: " + ", ".join(mt["attendants"]))
            if mt["hangoutLink"]:
                lines.append(STRINGS["link_label"].format(link=mt["hangoutLink"]))
            if mt["location"]:
                lines.append(STRINGS["location_label"].format(location=mt["location"]))
            if mt["description"]:
                lines.append(STRINGS["description_label"].format(description=mt["description"]))
            lines.append("")
        if lines[-1] == "":
            lines.pop()
        lines.append("")
    if lines and lines[-1] == "":
        lines.pop()

    if not lines:
        return STRINGS["no_meetings"]
    return "\n".join(lines)

def formatted_meeting(meeting, user_timezone='Europe/Kiev'):
    """Format meeting details with timezone-aware times."""
    lines = []
    title = meeting["title"]
    time_str = format_meeting_time(meeting, user_timezone)

    lines.append(title)
    lines.append(time_str)

    if meeting["attendants"]:
        lines.append("Участники: " + ", ".join(meeting["attendants"]))
    if meeting["hangoutLink"]:
        lines.append(STRINGS["link_label"].format(link=meeting["hangoutLink"]))
    if meeting["location"]:
        lines.append(STRINGS["location_label"].format(location=meeting["location"]))
    if meeting["description"]:
        lines.append(STRINGS["description_label"].format(description=meeting["description"]))

    return "\n".join(lines)