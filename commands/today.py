import datetime
import pytz
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from calendar_service import get_calendar_meetings
from event_formatter import format_meeting

def send_today_meetings(update: Update, context: CallbackContext):
    """Sends today's meetings to the Telegram chat."""
    chat_id = update.effective_chat.id

    thailand_tz = pytz.timezone('Asia/Bangkok')
    ukraine_tz = pytz.timezone('Europe/Kiev')

    now = datetime.datetime.now(thailand_tz)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_today = start_of_today + datetime.timedelta(days=1)

    today_meetings = get_calendar_meetings(start_of_today, end_of_today)

    if not today_meetings:
        context.bot.send_message(chat_id=chat_id, text='Немає зустрічей на сьогодні з кольором ID 5.')
    else:
        message = "Зустрічі на сьогодні:\n"
        for meeting in today_meetings:
            message += f"{format_meeting(meeting, thailand_tz, ukraine_tz)}\n"

        context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN) 