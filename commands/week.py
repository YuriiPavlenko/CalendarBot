import datetime
import pytz
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from calendar_service import get_calendar_meetings
from event_formatter import format_meeting

def send_week_meetings(update: Update, context: CallbackContext):
    """Sends all meetings for the current week to the Telegram chat."""
    chat_id = update.effective_chat.id

    thailand_tz = pytz.timezone('Asia/Bangkok')
    ukraine_tz = pytz.timezone('Europe/Kiev')

    now = datetime.datetime.now(thailand_tz)
    start_of_week = now - datetime.timedelta(days=now.weekday())  # Start of the week (Monday)
    end_of_week = start_of_week + datetime.timedelta(days=7)  # End of the week (Sunday)

    meetings = get_calendar_meetings(start_of_week, end_of_week)

    if not meetings:
        context.bot.send_message(chat_id=chat_id, text='Немає зустрічей на цей тиждень з кольором ID 5.')
    else:
        message = "Зустрічі на цей тиждень:\n"
        days_of_week = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П’ятниця', 'Субота', 'Неділя']
        current_day = None

        for meeting in meetings:
            meeting_day = meeting['start'].get('dateTime', meeting['start'].get('date'))
            meeting_day = datetime.datetime.fromisoformat(meeting_day).astimezone(thailand_tz).weekday()

            if current_day != meeting_day:
                current_day = meeting_day
                message += f"\n*{days_of_week[current_day]}:*\n"

            message += f"{format_meeting(meeting, thailand_tz, ukraine_tz)}\n"

        context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN) 