import datetime
import pytz
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from calendar_service import get_calendar_meetings
from commands.settings import get_user_language
from localization import get_texts

def send_week_meetings(update: Update, context: CallbackContext):
    """Sends all meetings for the current week to the Telegram chat."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    texts = get_texts(language)

    thailand_tz = pytz.timezone('Asia/Bangkok')
    ukraine_tz = pytz.timezone('Europe/Kiev')

    now = datetime.datetime.now(thailand_tz)
    start_of_week = now - datetime.timedelta(days=now.weekday())  # Start of the week (Monday)
    end_of_week = start_of_week + datetime.timedelta(days=7)  # End of the week (Sunday)

    meetings = get_calendar_meetings(start_of_week, end_of_week)

    message = f"**{texts['meetings_this_week'].strip().upper()}**\n\n"
    days_of_week = texts['days_of_week']
    current_day = None
    day_meetings = {i: [] for i in range(7)}

    for meeting in meetings:
        meeting_day = meeting.start.astimezone(thailand_tz).weekday()
        day_meetings[meeting_day].append(meeting)

    for day in range(7):
        message += f"*{days_of_week[day].upper()}*:\n\n"
        if not day_meetings[day]:
            message += texts['no_meetings'] + "\n\n"
        else:
            for meeting in day_meetings[day]:
                message += meeting.format(thailand_tz, ukraine_tz, language) + "\n"
            message += "\n"

    context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN) 