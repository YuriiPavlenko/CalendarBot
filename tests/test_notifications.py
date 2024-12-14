import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import Mock, patch, AsyncMock
from dateutil import tz

pytest_plugins = ['pytest_asyncio']

from src.notifications import (
    safe_get_meeting_data, 
    normalize_datetime,
    compare_datetimes,
    send_notification,
    refresh_meetings,
    notification_job
)
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserSettingsModel(Base):
    __tablename__ = "user_settings"
    user_id = Column(Integer, primary_key=True)
    notify_1h = Column(Boolean, default=False)
    notify_15m = Column(Boolean, default=False)
    notify_5m = Column(Boolean, default=False)
    username = Column(String)
    notify_new = Column(Boolean, default=False)
    filter_by_attendant = Column(Boolean, default=False)

class MeetingModel(Base):
    __tablename__ = "meetings"
    id = Column(String, primary_key=True)
    title = Column(String)
    start_time = Column(DateTime)  # UTC time
    end_time = Column(DateTime)    # UTC time
    attendants = Column(String)
    hangoutLink = Column(String)
    location = Column(String)
    description = Column(String)
    updated = Column(String)

@pytest.fixture
def sample_meeting_dict():
    return {
        "id": "36828kaerpn17l08dma0gdd09f_20241217T080000Z",
        "title": "Штурм иконок",
        "start_ua": datetime(2024, 12, 17, 15, 0, tzinfo=UTC),
        "end_ua": datetime(2024, 12, 17, 16, 0, tzinfo=UTC),
        "start_th": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Asia/Bangkok')),
        "end_th": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Asia/Bangkok')),
        "attendants": ["@ohshtein", "@romann_92", "@koshkooo", "@emerel", "@barslav", "@hmerijes"],
        "hangoutLink": "https://meet.google.com/etc-wqwm-ege",
        "description": "",
        "updated": "2024-12-12T16:59:47.499Z"
    }

@pytest.fixture
def sample_meeting_obj():
    meeting = MeetingModel()
    meeting.id = "e83ofps6ljkshume7jbvabs1mc"
    meeting.title = "Тест2"
    meeting.start_time = datetime(2024, 12, 20, 10, 15, tzinfo=UTC)
    meeting.end_time = datetime(2024, 12, 20, 11, 45, tzinfo=UTC)
    meeting.attendants = ""
    meeting.hangoutLink = ""
    meeting.location = ""
    meeting.description = ""
    meeting.updated = "2024-12-13T07:26:51.647Z"
    return meeting

@pytest.fixture
def mock_bot():
    return AsyncMock()

@pytest.fixture
def mock_session():
    session = Mock()
    # Configure query mock to return a query object with delete method
    query_mock = Mock()
    query_mock.delete = Mock(return_value=None)  # Ensure delete returns something
    query_mock.all = Mock(return_value=[])  # Default to empty list
    query_mock.filter = Mock(return_value=query_mock)  # Support filter chaining
    session.query.return_value = query_mock
    session.commit = Mock()
    session.close = Mock()
    return session

@pytest.fixture(autouse=True)
def mock_create_engine():
    with patch('database.create_engine') as mock_engine:  # Updated path
        mock_engine.return_value = create_engine('sqlite:///:memory:')
        yield mock_engine

@pytest.fixture(autouse=True)
def mock_database_url():
    with patch('database.DATABASE_URL', 'sqlite:///:memory:'):  # Updated path
        yield

def test_safe_get_meeting_data_dict(sample_meeting_dict):
    assert safe_get_meeting_data(sample_meeting_dict, "id") == "36828kaerpn17l08dma0gdd09f_20241217T080000Z"
    assert safe_get_meeting_data(sample_meeting_dict, "title") == "Штурм иконок"
    assert safe_get_meeting_data(sample_meeting_dict, "nonexistent", "default") == "default"

def test_safe_get_meeting_data_obj(sample_meeting_obj):
    assert safe_get_meeting_data(sample_meeting_obj, "id") == "e83ofps6ljkshume7jbvabs1mc"
    assert safe_get_meeting_data(sample_meeting_obj, "title") == "Тест2"
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

def test_normalize_datetime_edge_cases():
    # Test with microseconds
    dt = datetime(2024, 12, 17, 15, 0, 0, 123456, tzinfo=UTC)
    assert normalize_datetime(dt).microsecond == 123456
    
    # Test with different timezone
    dt = datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Asia/Bangkok'))
    normalized = normalize_datetime(dt)
    assert normalized.tzinfo == tz.UTC
    
    # Test with string input
    assert normalize_datetime("2024-12-17") == "2024-12-17"

@pytest.mark.asyncio
async def test_send_notification(mock_bot):
    with patch('src.notifications.bot', mock_bot):
        meeting = {"id": "123", "title": "Test"}
        await send_notification(123, meeting)
        mock_bot.send_message.assert_called_once()

@pytest.mark.asyncio
async def test_send_notification_invalid_data(mock_bot):
    with patch('src.notifications.bot', mock_bot):
        # Test with None meeting
        await send_notification(123, None)
        mock_bot.send_message.assert_not_called()
        
        # Test with empty meeting
        await send_notification(123, {})
        mock_bot.send_message.assert_not_called()
        
        # Test with None user_id
        await send_notification(None, {"title": "Test"})
        mock_bot.send_message.assert_not_called()

@pytest.mark.asyncio
async def test_send_notification_formatting_error(mock_bot):
    with patch('src.notifications.bot', mock_bot):
        # Test with invalid datetime
        meeting = {
            "title": "Test",
            "start_time": "invalid_datetime",
            "end_time": "invalid_datetime"
        }
        await send_notification(123, meeting)
        mock_bot.send_message.assert_not_called()

@pytest.mark.asyncio
async def test_refresh_meetings_new_meeting(mock_create_engine, mock_session, sample_meeting_dict):
    query_mock = mock_session.query.return_value
    query_mock.all.side_effect = [
        [],  # First call for UserSettings.notify_new
        [],  # Second call for Meeting.all
    ]
    
    with patch('src.notifications.SessionLocal', return_value=mock_session), \
         patch('src.notifications.fetch_meetings_from_gcal', return_value=[sample_meeting_dict]):
        await refresh_meetings()
        
        # Verify the calls
        query_mock.delete.assert_called_once()
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_refresh_meetings_updated_meeting(mock_create_engine, mock_session, sample_meeting_dict):
    existing_meeting = MeetingModel(
        id="36828kaerpn17l08dma0gdd09f_20241217T080000Z",
        title="Old Title",
        start_time=datetime(2024, 12, 17, 15, 0, tzinfo=UTC),
        end_time=datetime(2024, 12, 17, 16, 0, tzinfo=UTC),
        attendants="@ohshtein,@romann_92",  # Different attendants to trigger update
        updated="2024-12-12T16:59:47.499Z"
    )
    
    query_mock = mock_session.query.return_value
    query_mock.all.side_effect = [
        [],  # First call for UserSettings.notify_new
        [existing_meeting],  # Second call for Meeting.all
    ]
    
    with patch('src.notifications.SessionLocal', return_value=mock_session), \
         patch('src.notifications.fetch_meetings_from_gcal', return_value=[sample_meeting_dict]):
        await refresh_meetings()
        
        # Verify the calls
        query_mock.delete.assert_called_once()
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_notification_job_edge_cases(mock_session):
    # Test with invalid start_time
    invalid_meeting = MeetingModel(
        id="test_id",
        title="Test Meeting",
        start_time=None,  # Invalid start time
        end_time=datetime.now(UTC)
    )
    
    query_mock = mock_session.query.return_value
    query_mock.all.side_effect = [
        [invalid_meeting],  # Meetings
        []  # Users
    ]
    
    with patch('src.notifications.SessionLocal', return_value=mock_session):
        await notification_job(None)
        # Should not raise any errors and skip invalid meeting

@pytest.mark.asyncio
async def test_notification_job_windows(mock_session, mock_bot):
    now = datetime.now(UTC)
    
    # Create meetings at different notification windows
    meetings = [
        MeetingModel(  # 60-minute window
            id="60min",
            title="60min Meeting",
            start_time=now + timedelta(minutes=60),
            end_time=now + timedelta(minutes=120)
        ),
        MeetingModel(  # 15-minute window
            id="15min",
            title="15min Meeting",
            start_time=now + timedelta(minutes=15),
            end_time=now + timedelta(minutes=75)
        ),
        MeetingModel(  # 5-minute window
            id="5min",
            title="5min Meeting",
            start_time=now + timedelta(minutes=5),
            end_time=now + timedelta(minutes=65)
        ),
        MeetingModel(  # Just outside window
            id="outside",
            title="Outside Window",
            start_time=now + timedelta(minutes=62),
            end_time=now + timedelta(minutes=122)
        )
    ]
    
    # Create test user with all notifications enabled
    user = UserSettingsModel(
        user_id=123,
        notify_1h=True,
        notify_15m=True,
        notify_5m=True
    )
    
    query_mock = mock_session.query.return_value
    query_mock.all.side_effect = [
        meetings,  # First call for meetings
        [user]    # Second call for users
    ]
    
    with patch('src.notifications.SessionLocal', return_value=mock_session), \
         patch('src.notifications.bot', mock_bot):
        await notification_job(None)
        
        # Should send notifications for meetings in windows, skip the outside one
        assert mock_bot.send_message.call_count == 3

@pytest.mark.asyncio
async def test_refresh_meetings_duplicate_ids(mock_session, sample_meeting_dict):
    # Test handling of duplicate meeting IDs
    duplicate_dict = sample_meeting_dict.copy()
    duplicate_dict["title"] = "Duplicate Meeting"
    
    query_mock = mock_session.query.return_value
    query_mock.all.side_effect = [
        [],  # UserSettings
        []   # Existing meetings
    ]
    
    with patch('src.notifications.SessionLocal', return_value=mock_session), \
         patch('src.notifications.fetch_meetings_from_gcal', 
               return_value=[sample_meeting_dict, duplicate_dict]):
        await refresh_meetings()
        
        # Should handle duplicates gracefully
        assert mock_session.add.call_count == 2
        mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_refresh_meetings_attendee_filtering(mock_session, sample_meeting_dict):
    # Test notification filtering by attendee
    user1 = UserSettingsModel(user_id=123, username="@ohshtein", notify_new=True, filter_by_attendant=True)
    user2 = UserSettingsModel(user_id=456, username="@nonattendee", notify_new=True, filter_by_attendant=True)
    
    query_mock = mock_session.query.return_value
    query_mock.all.side_effect = [
        [user1, user2],  # UserSettings
        []  # Existing meetings
    ]
    
    with patch('src.notifications.SessionLocal', return_value=mock_session), \
         patch('src.notifications.fetch_meetings_from_gcal', return_value=[sample_meeting_dict]), \
         patch('src.notifications.send_notification') as mock_send:
        await refresh_meetings()
        
        # Should only notify user1 who is in attendees
        assert mock_send.call_count == 1
        mock_send.assert_called_with(123, sample_meeting_dict, is_new=True)
