import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from dateutil import tz
from src.notifications import (
    safe_get_meeting_data, 
    normalize_datetime,
    compare_datetimes,
    send_notification,
    refresh_meetings
)
from src.database import Meeting, UserSettings

@pytest.fixture
def sample_meeting_dict():
    return {
        "id": "123",
        "title": "Test Meeting",
        "start_ua": datetime.now(tz.UTC),
        "end_ua": datetime.now(tz.UTC) + timedelta(hours=1),
        "start_th": datetime.now(tz.gettz('Asia/Bangkok')),
        "end_th": datetime.now(tz.gettz('Asia/Bangkok')) + timedelta(hours=1),
        "attendants": ["@user1", "@user2"],
        "location": "Room 1",
        "hangoutLink": "https://meet.google.com/123",
        "description": "Test description",
        "updated": "2023-01-01T00:00:00Z"
    }

@pytest.fixture
def sample_meeting_obj():
    meeting = Meeting()
    meeting.id = "123"
    meeting.title = "Test Meeting"
    meeting.start_time = datetime.now(tz.UTC)
    meeting.end_time = datetime.now(tz.UTC) + timedelta(hours=1)
    meeting.attendants = "@user1,@user2"
    meeting.location = "Room 1"
    return meeting

@pytest.fixture
def mock_bot():
    return AsyncMock()

@pytest.fixture
def mock_session():
    session = Mock()
    session.query = Mock()
    session.commit = Mock()
    session.close = Mock()
    return session

def test_safe_get_meeting_data_dict(sample_meeting_dict):
    assert safe_get_meeting_data(sample_meeting_dict, "id") == "123"
    assert safe_get_meeting_data(sample_meeting_dict, "title") == "Test Meeting"
    assert safe_get_meeting_data(sample_meeting_dict, "nonexistent", "default") == "default"

def test_safe_get_meeting_data_obj(sample_meeting_obj):
    assert safe_get_meeting_data(sample_meeting_obj, "id") == "123"
    assert safe_get_meeting_data(sample_meeting_obj, "title") == "Test Meeting"
    assert safe_get_meeting_data(sample_meeting_obj, "nonexistent", "default") == "default"

def test_safe_get_meeting_data_with_none():
    assert safe_get_meeting_data(None, "any_field") is None
    assert safe_get_meeting_data(None, "any_field", "default") == "default"

def test_normalize_datetime():
    # Test with naive datetime
    naive_dt = datetime.now()
    normalized = normalize_datetime(naive_dt)
    assert normalized.tzinfo == tz.UTC

    # Test with aware datetime
    aware_dt = datetime.now(tz.gettz('Europe/Kiev'))
    normalized = normalize_datetime(aware_dt)
    assert normalized.tzinfo == tz.UTC

    # Test with None
    assert normalize_datetime(None) is None

def test_normalize_datetime_invalid():
    assert normalize_datetime("not a datetime") == "not a datetime"
    assert normalize_datetime(None) is None

def test_compare_datetimes():
    dt1 = datetime.now(tz.UTC)
    dt2 = dt1.astimezone(tz.gettz('Europe/Kiev'))
    assert compare_datetimes(dt1, dt2) == True

    dt3 = dt1 + timedelta(minutes=1)
    assert compare_datetimes(dt1, dt3) == False

@pytest.mark.asyncio
async def test_send_notification(mock_bot):
    with patch('src.notifications.bot', mock_bot):
        meeting = {"id": "123", "title": "Test"}
        await send_notification(123, meeting)
        mock_bot.send_message.assert_called_once()

@pytest.mark.asyncio
async def test_refresh_meetings_new_meeting(mock_session, sample_meeting_dict):
    with patch('src.notifications.SessionLocal', return_value=mock_session), \
         patch('src.notifications.fetch_meetings_from_gcal', return_value=[sample_meeting_dict]):
        
        mock_session.query().all.return_value = []  # No existing meetings
        await refresh_meetings()
        
        # Verify that delete and add were called
        mock_session.query().delete.assert_called_once()
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_refresh_meetings_updated_meeting(mock_session, sample_meeting_dict):
    existing_meeting = Meeting(
        id="123",
        title="Old Title",
        start_time=datetime.now(tz.UTC),
        end_time=datetime.now(tz.UTC) + timedelta(hours=1),
        attendants="@user1",
        updated="2023-01-01T00:00:00Z"
    )
    
    with patch('src.notifications.SessionLocal', return_value=mock_session), \
         patch('src.notifications.fetch_meetings_from_gcal', return_value=[sample_meeting_dict]):
        
        mock_session.query().all.return_value = [existing_meeting]
        await refresh_meetings()
        
        mock_session.query().delete.assert_called_once()
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
