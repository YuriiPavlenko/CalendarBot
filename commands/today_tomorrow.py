import datetime
import pytz
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from calendar_service import get_calendar_events
from event_formatter import format_event

def send_today_tomorrow_events(update: Update, context: CallbackContext):
    """Sends today's and tomorrow's events to the Telegram chat."""
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    bot = context.bot

    thailand_tz = pytz.timezone('Asia/Bangkok')
    ukraine_tz = pytz.timezone('Europe/Kiev')

    now = datetime.datetime.now(thailand_tz)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_tomorrow = start_of_today + datetime.timedelta(days=2)

    today_events = []
    tomorrow_events = []

    events = get_calendar_events(start_of_today, end_of_tomorrow)

    for event in events:
        start_time = datetime.datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
        if start_of_today <= start_time < start_of_today + datetime.timedelta(days=1):
            today_events.append(event)
        elif start_of_today + datetime.timedelta(days=1) <= start_time < end_of_tomorrow:
            tomorrow_events.append(event)

    if not today_events and not tomorrow_events:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text='Немає подій на сьогодні та завтра з кольором ID 5.')
    else:
        message = "Події на сьогодні:\n"
        for event in today_events:
            message += f"{format_event(event, thailand_tz, ukraine_tz)}\n"

        message += "\nПодії на завтра:\n"
        for event in tomorrow_events:
            message += f"{format_event(event, thailand_tz, ukraine_tz)}\n"

        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN) 