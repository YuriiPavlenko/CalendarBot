import os
import datetime
import json
import pytz
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from telegram import Update, Bot
from telegram.ext import CommandHandler, Updater, CallbackContext

# Define the scopes for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_service_account_credentials():
    """Constructs Google API credentials from a service account JSON key."""
    service_account_info = json.loads(os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY'))
    credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    return credentials

def get_calendar_events():
    """Fetches today's and tomorrow's events from a shared Google Calendar."""
    creds = get_service_account_credentials()
    service = build('calendar', 'v3', credentials=creds)

    # Define the time range for today and tomorrow in Thailand time zone
    thailand_tz = pytz.timezone('Asia/Bangkok')
    now = datetime.datetime.now(thailand_tz)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_tomorrow = start_of_today + datetime.timedelta(days=2)

    try:
        # Use the specific calendar ID of the shared calendar
        calendar_id = 'hmerijes@gmail.com'
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_of_today.isoformat(),
            timeMax=end_of_tomorrow.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        print("Fetched events:", events)  # Debugging line

        return events

    except Exception as e:
        print("Error fetching events:", e)
        return []

def send_events(update: Update, context: CallbackContext):
    """Sends today's and tomorrow's events to the Telegram chat."""
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    bot = context.bot

    events = get_calendar_events()
    if not events:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text='Немає подій на сьогодні та завтра з кольором ID 5.')
    else:
        message = "Події на сьогодні та завтра:\n"
        for event in events:
            message += f"- {event['summary']}\n"
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def main():
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL').rstrip('/')

    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command to fetch events
    dispatcher.add_handler(CommandHandler('getevents', send_events))

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=443,
                          url_path=TELEGRAM_BOT_TOKEN,
                          webhook_url=f"{TELEGRAM_WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}")

    updater.idle()

if __name__ == '__main__':
    main()
