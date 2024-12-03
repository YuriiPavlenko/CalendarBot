import os
import json
import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from localization import get_texts

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_service_account_credentials():
    """Constructs Google API credentials from a service account JSON key."""
    service_account_info = json.loads(os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY'))
    credentials = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    return credentials

class Meeting:
    def __init__(self, start, end, summary, goal=None, attendants=None, location=None, meet_link=None):
        self.start = datetime.datetime.fromisoformat(start['dateTime'])
        self.end = datetime.datetime.fromisoformat(end['dateTime'])
        self.summary = summary
        self.goal = goal
        self.attendants = attendants or []
        self.location = location
        self.meet_link = meet_link

    def format(self, thailand_tz, ukraine_tz, language):
        # Format the meeting details based on the selected language
        start_time_thailand = self.start.astimezone(thailand_tz).strftime('%H:%M')
        end_time_thailand = self.end.astimezone(thailand_tz).strftime('%H:%M')
        start_time_ukraine = self.start.astimezone(ukraine_tz).strftime('%H:%M')
        end_time_ukraine = self.end.astimezone(ukraine_tz).strftime('%H:%M')

        texts = get_texts(language)

        formatted_meeting = (
            f"*{self.summary}*\n"
            f"{texts['time_thailand']}: {start_time_thailand} - {end_time_thailand}\n"
            f"{texts['time_ukraine']}: {start_time_ukraine} - {end_time_ukraine}\n"
        )

        if self.goal:
            formatted_meeting += f"{texts['goal']}: {self.goal}\n"
        if self.attendants:
            formatted_meeting += f"{texts['attendants']}: {', '.join(self.attendants)}\n"
        if self.location:
            formatted_meeting += f"{texts['location']}: {self.location}\n"
        if self.meet_link:
            formatted_meeting += f"{texts['meet_link']}: {self.meet_link}\n"

        return formatted_meeting

def get_calendar_meetings(time_min, time_max):
    """Fetches meetings from the Google Calendar within a specified time range."""
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

        meetings = []
        for event in events_result.get('items', []):
            if event.get('colorId') == '5':  # Internal filter
                meeting = Meeting(
                    start=event['start'],
                    end=event['end'],
                    summary=event.get('summary', 'No Title'),
                    goal=event.get('description'),
                    attendants=[attendee.get('email') for attendee in event.get('attendees', [])],
                    location=event.get('location'),
                    meet_link=event.get('hangoutLink')
                )
                meetings.append(meeting)
        return meetings

    except Exception as e:
        print("Error fetching meetings:", e)
        return [] 