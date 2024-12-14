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
    refresh_meetings
)
from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

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
    with patch('src.database.create_engine') as mock_engine:
        mock_engine.return_value = create_engine('sqlite:///:memory:')
        yield mock_engine

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

@pytest.mark.asyncio
async def test_send_notification(mock_bot):
    with patch('src.notifications.bot', mock_bot):
        meeting = {"id": "123", "title": "Test"}
        await send_notification(123, meeting)
        mock_bot.send_message.assert_called_once()

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
