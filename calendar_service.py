import os
import json
import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_service_account_credentials():
    """Constructs Google API credentials from a service account JSON key."""
    service_account_info = json.loads(os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY'))
    credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    return credentials

def get_calendar_meetings(time_min, time_max):
    """Fetches meetings with color ID 5 from the Google Calendar within a specified time range."""
    creds = get_service_account_credentials()
    service = build('calendar', 'v3', credentials=creds)

    try:
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        # Filter events by color ID 5 and add goal and attendants
        meetings = []
        for event in events_result.get('items', []):
            if event.get('colorId') == '5':
                meeting = {
                    'start': event['start'],
                    'end': event['end'],
                    'summary': event.get('summary', 'No Title'),
                    'goal': event.get('description', 'No Description'),
                    'attendants': [attendee.get('email') for attendee in event.get('attendees', [])]
                }
                meetings.append(meeting)
        return meetings

    except Exception as e:
        print("Error fetching meetings:", e)
        return [] 