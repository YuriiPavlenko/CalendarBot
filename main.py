import os
import datetime
import json
import pytz
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from telegram import Update, Bot, ParseMode
from telegram.ext import CommandHandler, Updater, CallbackContext

# Define the scopes for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_service_account_credentials():
    """Constructs Google API credentials from a service account JSON key."""
    service_account_info = json.loads(os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY'))
    credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    return credentials

def get_calendar_events(time_min, time_max):
    """Fetches events with color ID 5 from the Google Calendar within a specified time range."""
    creds = get_service_account_credentials()
    service = build('calendar', 'v3', credentials=creds)

    try:
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID')  # Use environment variable for calendar ID
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        print("Fetched events:", events)  # Debugging line

        # Filter events by color ID 5
        filtered_events = [event for event in events if event.get('colorId') == '5']
        print("Filtered events:", filtered_events)  # Debugging line

        return filtered_events

    except Exception as e:
        print("Error fetching events:", e)
        return []

def format_event(event, thailand_tz, ukraine_tz):
    """Formats the event time for display in both Thailand and Ukraine time zones."""
    start_time = datetime.datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
    end_time = datetime.datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
    start_time_thailand = start_time.astimezone(thailand_tz).strftime('%H:%M')
    end_time_thailand = end_time.astimezone(thailand_tz).strftime('%H:%M')
    start_time_ukraine = start_time.astimezone(ukraine_tz).strftime('%H:%M')
    end_time_ukraine = end_time.astimezone(ukraine_tz).strftime('%H:%M')

    location = event.get('location', '')
    hangout_link = event.get('hangoutLink', '')

    location_info = f"Місце: {location}" if location else f"Посилання на зустріч: {hangout_link}" if hangout_link else ""

    return (
        f"*{event['summary']}*\n"
        f"Час у Таїланді: {start_time_thailand} - {end_time_thailand}\n"
        f"Час в Україні: {start_time_ukraine} - {end_time_ukraine}\n"
        f"{location_info}\n"
    )

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

def send_week_events(update: Update, context: CallbackContext):
    """Sends all events for the current week to the Telegram chat."""
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    bot = context.bot

    thailand_tz = pytz.timezone('Asia/Bangkok')
    ukraine_tz = pytz.timezone('Europe/Kiev')

    now = datetime.datetime.now(thailand_tz)
    start_of_week = now - datetime.timedelta(days=now.weekday())  # Start of the week (Monday)
    end_of_week = start_of_week + datetime.timedelta(days=7)  # End of the week (Sunday)

    events = get_calendar_events(start_of_week, end_of_week)

    if not events:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text='Немає подій на цей тиждень з кольором ID 5.')
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

        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)

def main():
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command to fetch today's and tomorrow's events
    dispatcher.add_handler(CommandHandler('getevents', send_today_tomorrow_events))

    # Command to fetch all events for the week
    dispatcher.add_handler(CommandHandler('getweekevents', send_week_events))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
