import datetime
import pytz
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from calendar_service import get_calendar_meetings
from commands.settings import get_user_language

def send_today_meetings(update: Update, context: CallbackContext):
    """Sends today's meetings to the Telegram chat."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    language = get_user_language(user_id)  # Retrieve language from the database

    thailand_tz = pytz.timezone('Asia/Bangkok')
    ukraine_tz = pytz.timezone('Europe/Kiev')

    now = datetime.datetime.now(thailand_tz)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = start_of_today + datetime.timedelta(days=1)

    today_meetings = get_calendar_meetings(start_of_today, end_of_today)

    if not today_meetings:
        context.bot.send_message(chat_id=chat_id, text="No meetings found.")
    else:
        message = "Meetings for today:\n"
        for meeting in today_meetings:
            message += meeting.format(thailand_tz, ukraine_tz, language) + "\n"

        context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN) 