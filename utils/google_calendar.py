from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

def get_calendar_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_meetings_for_period(period, username=None):
    service = get_calendar_service()
    # Implement logic to fetch meetings for the specified period
    # Optionally filter by username if provided
    return []

def create_calendar_event(title, start_time, end_time, location, attendees):
    service = get_calendar_service()
    event = {
        'summary': title,
        'location': location,
        'start': {
            'dateTime': start_time,
            'timeZone': 'Europe/Kiev',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Europe/Kiev',
        },
        'attendees': [{'email': email.strip()} for email in attendees],
    }
    event = service.events().insert(calendarId='primary', body=event).execute()
    return event
