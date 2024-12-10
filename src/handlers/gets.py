import logging
from telegram import Update
from telegram.ext import ContextTypes
from ..database import SessionLocal, get_user_settings
from ..google_calendar import fetch_meetings
from ..localization import STRINGS
from ..utils import filter_meetings, format_meetings_list
from ..utils import get_today_th, get_tomorrow_th, get_rest_week_th, get_next_week_th

logger = logging.getLogger(__name__)

async def get_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("/get_today command invoked")
    user_id = update.effective_user.id
    username = f"@{update.effective_user.username}" if update.effective_user.username else f"@{user_id}"
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    filter_type = us.filter_type
    session.close()

    start, end = get_today_th()
    meetings = fetch_meetings(start, end)
    meetings = filter_meetings(meetings, filter_type, username)

    text = format_meetings_list(meetings, period="today") if meetings else STRINGS["no_meetings"]
    logger.debug("Responding to /get_today with %d meetings", len(meetings))
    await update.message.reply_text(text, parse_mode='Markdown')

async def get_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("/get_tomorrow command invoked")
    user_id = update.effective_user.id
    username = f"@{update.effective_user.username}" if update.effective_user.username else f"@{user_id}"
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    filter_type = us.filter_type
    session.close()

    start, end = get_tomorrow_th()
    meetings = fetch_meetings(start, end)
    meetings = filter_meetings(meetings, filter_type, username)

    text = format_meetings_list(meetings, period="tomorrow") if meetings else STRINGS["no_meetings"]
    logger.debug("Responding to /get_tomorrow with %d meetings", len(meetings))
    await update.message.reply_text(text, parse_mode='Markdown')

async def get_rest_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("/get_rest_week command invoked")
    user_id = update.effective_user.id
    username = f"@{update.effective_user.username}" if update.effective_user.username else f"@{user_id}"
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    filter_type = us.filter_type
    session.close()

    start, end = get_rest_week_th()
    meetings = fetch_meetings(start, end)
    meetings = filter_meetings(meetings, filter_type, username)

    text = format_meetings_list(meetings, period="week") if meetings else STRINGS["no_meetings"]
    logger.debug("Responding to /get_rest_week with %d meetings", len(meetings))
    await update.message.reply_text(text, parse_mode='Markdown')

async def get_next_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("/get_next_week command invoked")
    user_id = update.effective_user.id
    username = f"@{update.effective_user.username}" if update.effective_user.username else f"@{user_id}"
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    filter_type = us.filter_type
    session.close()

    start, end = get_next_week_th()
    meetings = fetch_meetings(start, end)
    meetings = filter_meetings(meetings, filter_type, username)

    text = format_meetings_list(meetings, period="week") if meetings else STRINGS["no_meetings"]
    logger.debug("Responding to /get_next_week with %d meetings", len(meetings))
    await update.message.reply_text(text, parse_mode='Markdown')
