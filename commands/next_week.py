import datetime
import pytz
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from calendar_service import get_calendar_meetings
from commands.settings import get_user_language

def send_next_week_meetings(update: Update, context: CallbackContext):
    """Sends next week's meetings to the Telegram chat."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    language = get_user_language(user_id)

    thailand_tz = pytz.timezone('Asia/Bangkok')
    ukraine_tz = pytz.timezone('Europe/Kiev')

    now = datetime.datetime.now(thailand_tz)
    start_of_next_week = now + datetime.timedelta(days=(7 - now.weekday()))  # Start of next week (Monday)
    end_of_next_week = start_of_next_week + datetime.timedelta(days=7)  # End of next week (Sunday)

    next_week_meetings = get_calendar_meetings(start_of_next_week, end_of_next_week)

    if not next_week_meetings:
        context.bot.send_message(chat_id=chat_id, text="No meetings found.")
    else:
        message = "Meetings for next week:\n"
        days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        current_day = None

        for meeting in next_week_meetings:
            meeting_day = meeting.start.astimezone(thailand_tz).weekday()

            if current_day != meeting_day:
                current_day = meeting_day
                message += f"\n*{days_of_week[current_day]}:*\n"

            message += meeting.format(thailand_tz, ukraine_tz, language) + "\n"

        context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN) 