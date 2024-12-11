import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from ..database import SessionLocal, get_user_settings
from ..utils import filter_meetings, get_today_th, get_tomorrow_th, get_rest_week_th, get_next_week_th
from ..cache import cache
from ..localization import STRINGS
from dateutil import tz
from ..config import TIMEZONE_TH

logger = logging.getLogger(__name__)

def format_meetings_list(meetings, period="today"):
    # Same code as before, no changes, just ensure we’re not referencing DB objects here.
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
        for mt in day_meetings:
            title = mt["title"]
            start_ua = mt["start_ua"].strftime("%H:%M")
            end_ua = mt["end_ua"].strftime("%H:%M")
            start_th = mt["start_th"].strftime("%H:%M")
            end_th = mt["end_th"].strftime("%H:%M")
            lines.append(f"{title}")
            lines.append(STRINGS["ukraine_time"].format(start=start_ua, end=end_ua))
            lines.append(STRINGS["thailand_time"].format(start=start_th, end=end_th))
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

async def get_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    # Extract needed attributes before closing the session
    filter_type = us.filter_type
    session.close()

    meetings = cache.get_meetings()
    start, end = get_today_th()
    todays = [m for m in meetings if m["start_th"] >= start and m["start_th"] < end]
    filtered = filter_meetings(todays, filter_type, f"@{user_id}")
    text = format_meetings_list(filtered, "today")
    await update.message.reply_text(text)

async def get_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    filter_type = us.filter_type
    session.close()

    meetings = cache.get_meetings()
    start, end = get_tomorrow_th()
    tomorrows = [m for m in meetings if m["start_th"] >= start and m["start_th"] < end]
    filtered = filter_meetings(tomorrows, filter_type, f"@{user_id}")
    text = format_meetings_list(filtered, "tomorrow")
    await update.message.reply_text(text)

async def get_rest_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    filter_type = us.filter_type
    session.close()

    meetings = cache.get_meetings()
    start, end = get_rest_week_th()
    filtered_range = [m for m in meetings if m["start_th"] >= start and m["start_th"] < end]
    filtered = filter_meetings(filtered_range, filter_type, f"@{user_id}")
    text = format_meetings_list(filtered, "week")
    await update.message.reply_text(text)

async def get_next_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    filter_type = us.filter_type
    session.close()

    meetings = cache.get_meetings()
    start, end = get_next_week_th()
    filtered_range = [m for m in meetings if m["start_th"] >= start and m["start_th"] < end]
    filtered = filter_meetings(filtered_range, filter_type, f"@{user_id}")
    text = format_meetings_list(filtered, "week")
    await update.message.reply_text(text)

get_today_handler = CommandHandler("get_today", get_today)
get_tomorrow_handler = CommandHandler("get_tomorrow", get_tomorrow)
get_rest_week_handler = CommandHandler("get_rest_week", get_rest_week)
get_next_week_handler = CommandHandler("get_next_week", get_next_week)
