import json
import datetime
from dateutil import parser, tz
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from src.config import GOOGLE_SERVICE_ACCOUNT_KEY, GOOGLE_CALENDAR_ID

def get_calendar_service():
    creds = Credentials.from_service_account_info(json.loads(GOOGLE_SERVICE_ACCOUNT_KEY))
    service = build('calendar', 'v3', credentials=creds)
    return service

def fetch_meetings(start_dt, end_dt):
    service = get_calendar_service()
    events_result = service.events().list(
        calendarId=GOOGLE_CALENDAR_ID,
        timeMin=start_dt.isoformat(),
        timeMax=end_dt.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    meetings = []
    for e in events:
        meetings.append(transform_event_to_meeting(e))
    return meetings

def transform_event_to_meeting(event):
    # Meeting structure:
    #   0. internal ID
    #   1. Title
    #   2. Start datetime in Ukraine
    #   3. Start datetime in Thailand
    #   4. End datetime in Ukraine
    #   5. End datetime in Thailand
    #   6. Attendants (list)
    #   7. Location
    #   8. Google meets link
    #   9. Description

    title = event.get('summary', '')
    description = event.get('description', '')
    start = parser.isoparse(event['start'].get('dateTime', event['start'].get('date')))
    end = parser.isoparse(event['end'].get('dateTime', event['end'].get('date')))
    # convert times to UA and TH
    ua_tz = tz.gettz("Europe/Kiev")
    th_tz = tz.gettz("Asia/Bangkok")
    start_ua = start.astimezone(ua_tz)
    start_th = start.astimezone(th_tz)
    end_ua = end.astimezone(ua_tz)
    end_th = end.astimezone(th_tz)

    attendees = event.get('attendees', [])
    attendants_list = []
    for a in attendees:
        email = a.get('email','')
        # If it's in format "1@nickname"
        # We just extract @nickname
        if "@" in email:
            # The first char may be '1', second should be nickname start
            # According to the requirement, format is "1@nickname"
            # so we return "@nickname"
            nickname_part = email.split('@',1)[1]
            attendants_list.append("@" + nickname_part)

    location = event.get('location', '')
    hangoutLink = event.get('hangoutLink', '')

    return {
        "id": event.get('id',''),
        "title": title,
        "start_ua": start_ua,
        "start_th": start_th,
        "end_ua": end_ua,
        "end_th": end_th,
        "attendants": attendants_list,
        "location": location,
        "hangoutLink": hangoutLink,
        "description": description
    }
