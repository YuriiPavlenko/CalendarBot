import json
from dateutil import parser, tz
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from config import GOOGLE_SERVICE_ACCOUNT_KEY, GOOGLE_CALENDAR_ID
from config import TIMEZONE_UA, TIMEZONE_TH

def get_calendar_service():
    creds = Credentials.from_service_account_info(json.loads(GOOGLE_SERVICE_ACCOUNT_KEY))
    service = build('calendar', 'v3', credentials=creds, cache_discovery=False)
    return service

def fetch_meetings_from_gcal(start_dt, end_dt):
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
    start = parser.isoparse(event['start'].get('dateTime', event['start'].get('date')))
    end = parser.isoparse(event['end'].get('dateTime', event['end'].get('date')))

    ua_tz = tz.gettz(TIMEZONE_UA)
    th_tz = tz.gettz(TIMEZONE_TH)
    start_ua = start.astimezone(ua_tz)
    start_th = start.astimezone(th_tz)
    end_ua = end.astimezone(ua_tz)
    end_th = end.astimezone(th_tz)

    attendees = event.get('attendees', [])
    attendants_list = []
    for a in attendees:
        email = a.get('email','')
        if '@' in email:
            # "1@nickname"
            parts = email.split('@',1)
            if len(parts) == 2:
                nick = parts[1]
                attendants_list.append("@"+nick)

    return {
        "id": event.get('id',''),
        "title": event.get('summary',''),
        "start_ua": start_ua,
        "start_th": start_th,
        "end_ua": end_ua,
        "end_th": end_th,
        "attendants": attendants_list,
        "location": event.get('location',''),
        "hangoutLink": event.get('hangoutLink',''),
        "description": event.get('description',''),
        "updated": event.get('updated','')
    }
