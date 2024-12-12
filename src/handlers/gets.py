import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from ..database import SessionLocal, get_user_settings, Meeting
from ..utils import filter_meetings, get_today_th, get_tomorrow_th, get_rest_week_th, get_next_week_th
from ..localization import STRINGS
from ..formatters import format_meetings_list

logger = logging.getLogger(__name__)

async def _get_meetings_for_period(update: Update, context: ContextTypes.DEFAULT_TYPE, period):
    user_id = update.effective_user.id
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    filter_type = us.filter_by_attendant
    user_identifier = us.username if us.username else f"@{user_id}"

    if period == "today":
        start, end = get_today_th()
    elif period == "tomorrow":
        start, end = get_tomorrow_th()
    elif period == "rest_week":
        start, end = get_rest_week_th()
    elif period == "next_week":
        start, end = get_next_week_th()

    meetings = session.query(Meeting).filter(Meeting.start_th >= start, Meeting.start_th < end).all()
    session.close()

    meetings_list = []
    for m in meetings:
        meeting = {
            "id": m.id,
            "title": m.title,
            "start_ua": m.start_ua,
            "end_ua": m.end_ua,
            "start_th": m.start_th,
            "end_th": m.end_th,
            "attendants": m.attendants.split(",") if m.attendants else [],
            "hangoutLink": m.hangoutLink,
            "location": m.location,
            "description": m.description,
            "updated": m.updated,
        }
        meetings_list.append(meeting)

    filtered = filter_meetings(meetings_list, filter_type, user_identifier)
    text = format_meetings_list(filtered, period)
    await update.message.reply_text(text)

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
