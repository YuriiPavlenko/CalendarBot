import pytest
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from dateutil import tz
from src.google_calendar import get_calendar_service, fetch_meetings_from_gcal, transform_event_to_meeting

@pytest.fixture
def sample_event():
    return {
        'id': 'event_id',
        'summary': 'Event Title',
        'start': {'dateTime': '2024-12-17T15:00:00+07:00'},
        'end': {'dateTime': '2024-12-17T16:00:00+07:00'},
        'attendees': [{'email': '1@nickname'}, {'email': '2@nickname'}],
        'location': 'Location',
        'hangoutLink': 'https://meet.google.com/link',
        'description': 'Description',
        'updated': '2024-12-12T16:59:47.499Z'
    }

@pytest.fixture
def mock_credentials():
    with patch('src.google_calendar.Credentials') as mock_creds:
        mock_creds.from_service_account_info.return_value = Mock()
        yield mock_creds

@pytest.fixture
def mock_service():
    mock = Mock()
    mock.events.return_value.list.return_value.execute.return_value = {
        'items': [{
            'id': 'test123',
            'summary': 'Test Meeting',
            'start': {'dateTime': '2024-12-17T15:00:00+07:00'},
            'end': {'dateTime': '2024-12-17T16:00:00+07:00'},
            'attendees': [{'email': '1@nickname'}],
            'location': 'Room 1',
            'hangoutLink': 'https://meet.google.com/123',
            'description': 'Test description',
            'updated': '2024-12-12T16:59:47.499Z'
        }]
    }
    return mock

def test_get_calendar_service(mock_credentials):
    with patch('src.google_calendar.build') as mock_build, \
         patch('src.google_calendar.json.loads') as mock_loads:
        mock_loads.return_value = {'type': 'service_account'}
        mock_build.return_value = Mock()
        
        service = get_calendar_service()
        assert mock_credentials.from_service_account_info.called
        assert mock_build.called
        assert service is not None

def test_fetch_meetings_from_gcal(mock_service):
    with patch('src.google_calendar.get_calendar_service', return_value=mock_service):
        start = datetime.now(tz.UTC)
        end = start + timedelta(days=1)
        meetings = fetch_meetings_from_gcal(start, end)
        assert len(meetings) == 1
        assert meetings[0]['id'] == 'test123'

def test_transform_event_to_meeting():
    event = {
        'id': 'test123',
        'summary': 'Test Meeting',
        'start': {'dateTime': '2024-12-17T15:00:00+07:00'},
        'end': {'dateTime': '2024-12-17T16:00:00+07:00'},
        'attendees': [{'email': '1@nickname'}],
        'location': 'Room 1',
        'hangoutLink': 'https://meet.google.com/123',
        'description': 'Test description',
        'updated': '2024-12-12T16:59:47.499Z'
    }
    
    meeting = transform_event_to_meeting(event)
    assert meeting['id'] == 'test23'
    assert meeting['title'] == 'Test Meeting'
    assert '@nickname' in meeting['attendants']
    assert meeting['location'] == 'Room 1'
    assert meeting['hangoutLink'] == 'https://meet.google.com/123'
    assert meeting['description'] == 'Test description'
