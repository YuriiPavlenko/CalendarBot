import datetime
import pytz
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from calendar_service import get_calendar_events
from event_formatter import format_event

def send_week_events(update: Update, context: CallbackContext):
    """Sends all events for the current week to the Telegram chat."""
    # Use the message object directly since this is a command handler
    chat_id = update.effective_chat.id

    thailand_tz = pytz.timezone('Asia/Bangkok')
    ukraine_tz = pytz.timezone('Europe/Kiev')

    now = datetime.datetime.now(thailand_tz)
    start_of_week = now - datetime.timedelta(days=now.weekday())  # Start of the week (Monday)
    end_of_week = start_of_week + datetime.timedelta(days=7)  # End of the week (Sunday)

    events = get_calendar_events(start_of_week, end_of_week)

    if not events:
        context.bot.send_message(chat_id=chat_id, text='Немає подій на цей тиждень.')
    else:
        message = "Події на цей тиждень:\n"
        days_of_week = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П’ятниця', 'Субота', 'Неділя']
        current_day = None

        for event in events:
            event_day = event['start'].get('dateTime', event['start'].get('date'))
            event_day = datetime.datetime.fromisoformat(event_day).astimezone(thailand_tz).weekday()

            if current_day != event_day:
                current_day = event_day
                message += f"\n*{days_of_week[current_day]}:*\n"

            message += f"{format_event(event, thailand_tz, ukraine_tz)}\n"

        context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN) 