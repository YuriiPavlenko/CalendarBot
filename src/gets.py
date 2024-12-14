import logging
from datetime import datetime, timedelta
from dateutil import tz
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from database import SessionLocal, Meeting
from .utils import get_today_th, get_tomorrow_th, get_rest_week_th, get_next_week_th  # Add relative import
from .localization import STRINGS  # Add relative import
from .formatters import format_meetings_list  # Add relative import
from .config import TIMEZONE_TH  # Add relative import

logger = logging.getLogger(__name__)

async def _get_meetings_for_period(update: Update, context: ContextTypes.DEFAULT_TYPE, period: str):
    session = SessionLocal()
    try:
        # Get time range in TH timezone
        if period == "today":
            start_th, end_th = get_today_th()
        elif period == "tomorrow":
            start_th, end_th = get_tomorrow_th()
        elif period == "rest_week":
            start_th, end_th = get_rest_week_th()
        else:  # next week
            start_th, end_th = get_next_week_th()

        # Convert to UTC for database query
        start_utc = start_th.astimezone(tz.UTC)
        end_utc = end_th.astimezone(tz.UTC)
        
        # Query using UTC times
        meetings = session.query(Meeting).filter(
            Meeting.start_time >= start_utc,
            Meeting.start_time < end_utc
        ).all()

        # Convert meetings to display format
        formatted_meetings = []
        for m in meetings:
            start_th = m.start_time.replace(tzinfo=tz.UTC).astimezone(tz.gettz(TIMEZONE_TH))
            end_th = m.end_time.replace(tzinfo=tz.UTC).astimezone(tz.gettz(TIMEZONE_TH)) if m.end_time else None
            start_ua = m.start_time.replace(tzinfo=tz.UTC).astimezone(tz.gettz('Europe/Kiev'))
            end_ua = m.end_time.replace(tzinfo=tz.UTC).astimezone(tz.gettz('Europe/Kiev')) if m.end_time else None
            
            formatted_meetings.append({
                "id": m.id,
                "title": m.title,
                "start_th": start_th,
                "end_th": end_th,
                "start_ua": start_ua,
                "end_ua": end_ua,
                "attendants": m.attendants.split(",") if m.attendants else [],
                "hangoutLink": m.hangoutLink,
                "location": m.location,
                "description": m.description,
            })

        text = format_meetings_list(formatted_meetings, period)
        await update.message.reply_text(text)
    finally:
        session.close()

async def get_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _get_meetings_for_period(update, context, "today")

async def get_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _get_meetings_for_period(update, context, "tomorrow")

async def get_rest_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _get_meetings_for_period(update, context, "rest_week")

async def get_next_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _get_meetings_for_period(update, context, "next_week")

get_today_handler = CommandHandler("get_today", get_today)
get_tomorrow_handler = CommandHandler("get_tomorrow", get_tomorrow)
get_rest_week_handler = CommandHandler("get_rest_week", get_rest_week)
get_next_week_handler = CommandHandler("get_next_week", get_next_week)
