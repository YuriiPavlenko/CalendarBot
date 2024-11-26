import os
import datetime
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from telegram import Bot, Update
from telegram.ext import CommandHandler, Updater

# Define the scopes for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_events():
    """Fetches today's and tomorrow's events with color ID 5 from the Google Calendar."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Define the time range for today and tomorrow
    now = datetime.datetime.utcnow()
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_tomorrow = start_of_today + datetime.timedelta(days=2)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=start_of_today.isoformat() + 'Z',
        timeMax=end_of_tomorrow.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    # Filter events by color ID 5
    filtered_events = [event for event in events if event.get('colorId') == '5']

    return filtered_events

def send_events(update: Update, context):
    """Sends today's and tomorrow's events to the Telegram chat."""
    events = get_calendar_events()
    if not events:
        update.message.reply_text('Немає подій на сьогодні та завтра з кольором ID 5.')
    else:
        message = "Події на сьогодні та завтра:\n"
        for event in events:
            message += f"- {event['summary']}\n"
        update.message.reply_text(message)

def main():
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command to fetch events
    dispatcher.add_handler(CommandHandler('getevents', send_events))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
