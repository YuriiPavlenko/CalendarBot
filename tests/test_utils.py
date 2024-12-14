import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import patch
from dateutil import tz
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base
from src.utils import (
    filter_meetings,
    get_today_th,
    get_tomorrow_th,
    get_rest_week_th,
    get_next_week_th,
    convert_meeting_to_display
)

@pytest.fixture
def sample_meetings():
    return [
        {
            "title": "Штурм иконок",
            "attendants": ["@ohshtein", "@romann_92", "@koshkooo", "@emerel", "@barslav", "@hmerijes"]
        },
        {
            "title": "Тест2",
            "attendants": ["@user3"]
        },
        {
            "title": "Another meeting",
            "attendants": ["@ohshtein"]
        }
    ]

def test_filter_meetings(sample_meetings):
    filtered = filter_meetings(sample_meetings, True, "@ohshtein")
    assert len(filtered) == 2
    assert all("@ohshtein" in m["attendants"] for m in filtered)

def test_filter_meetings_edge_cases():
    meetings = [
        {"attendants": None},  # No attendants field
        {"attendants": []},    # Empty attendants
        {},                    # Empty meeting
        {"attendants": ["@user1", "@user2"]}   # Valid meeting
    ]
    
    filtered = filter_meetings(meetings, True, "@user1")
    assert len(filtered) == 1
    assert filtered[0]["attendants"] == ["@user1", "@user2"]
    
    # Test with filter off
    assert len(filter_meetings(meetings, False, "@user1")) == 4

def test_get_today_th():
    start, end = get_today_th()
    assert end - start == timedelta(days=1)
    assert start.tzinfo == tz.gettz('Asia/Bangkok')

def test_get_today_th_edge_cases():
    # Test around midnight
    with patch('src.utils.datetime') as mock_dt:
        mock_dt.now.return_value = datetime(2024, 12, 17, 23, 59, tzinfo=tz.gettz('Asia/Bangkok'))
        start, end = get_today_th()
        assert start.day == 17
        assert end.day == 18
        assert start.hour == 0
        assert end.hour == 0
        
        # Test just after midnight
        mock_dt.now.return_value = datetime(2024, 12, 18, 0, 1, tzinfo=tz.gettz('Asia/Bangkok'))
        start, end = get_today_th()
        assert start.day == 18
        assert end.day == 19

def test_get_tomorrow_th():
    start, end = get_tomorrow_th()
    assert end - start == timedelta(days=1)
    assert start > datetime.now(tz.gettz('Asia/Bangkok'))

def test_get_tomorrow_th_edge_cases():
    # Test DST transition
    with patch('src.utils.datetime') as mock_dt:
        # Simulate DST transition
        mock_dt.now.return_value = datetime(2024, 3, 30, 23, 0, tzinfo=tz.gettz('Asia/Bangkok'))
        start, end = get_tomorrow_th()
        assert (end - start).total_seconds() == 86400  # Should still be 24 hours
        
        # Test year boundary
        mock_dt.now.return_value = datetime(2024, 12, 31, 23, 0, tzinfo=tz.gettz('Asia/Bangkok'))
        start, end = get_tomorrow_th()
        assert start.year == 2025
        assert end.year == 2025

def test_get_rest_week_th_edge_cases():
    # Test Friday
    with patch('src.utils.datetime') as mock_dt:
        mock_dt.now.return_value = datetime(2024, 12, 20, 15, 0, tzinfo=tz.gettz('Asia/Bangkok'))  # Friday
        start, end = get_rest_week_th()
        assert (end - start).days == 1  # Should only return today's range
        
        # Test Saturday
        mock_dt.now.return_value = datetime(2024, 12, 21, 15, 0, tzinfo=tz.gettz('Asia/Bangkok'))  # Saturday
        start, end = get_rest_week_th()
        assert (end - start).days == 1  # Should only return today's range
        
        # Test Monday
        mock_dt.now.return_value = datetime(2024, 12, 16, 15, 0, tzinfo=tz.gettz('Asia/Bangkok'))  # Monday
        start, end = get_rest_week_th()
        assert (end - start).days == 5  # Should return full work week

def test_get_next_week_th_edge_cases():
    # Test Sunday
    with patch('src.utils.datetime') as mock_dt:
        mock_dt.now.return_value = datetime(2024, 12, 22, 15, 0, tzinfo=tz.gettz('Asia/Bangkok'))  # Sunday
        start, end = get_next_week_th()
        assert start.day == 23  # Next Monday
        assert (end - start).days == 5  # Full work week
        
        # Test Friday
        mock_dt.now.return_value = datetime(2024, 12, 20, 15, 0, tzinfo=tz.gettz('Asia/Bangkok'))  # Friday
        start, end = get_next_week_th()
        assert start.day == 23  # Next Monday
        assert end.day == 28    # Next Friday

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

def test_convert_meeting_to_display():
    meeting = MeetingModel(
        id="123",
        title="Test",
        start_time=datetime.now(UTC),
        end_time=datetime.now(UTC) + timedelta(hours=1),
        attendants="@user1,@user2",
        location="Room 1"
    )
    
    result = convert_meeting_to_display(meeting)
    assert result["id"] == "123"
    assert "start_ua" in result
    assert "start_th" in result
    assert isinstance(result["attendants"], list)

def test_convert_meeting_to_display_edge_cases():
    # Test with missing fields
    meeting = MeetingModel(
        id="test",
        title=None,
        start_time=datetime.now(UTC),
        end_time=None,
        attendants=None,
        description=None
    )
    result = convert_meeting_to_display(meeting)
    assert result["title"] is None
    assert "end_ua" in result
    assert result["attendants"] == []
    
    # Test with invalid timezone
    meeting = MeetingModel(
        id="test",
        title="Test Meeting",
        start_time=datetime.now(),  # Naive datetime
        end_time=datetime.now(),    # Naive datetime
        attendants="@user1"
    )
    result = convert_meeting_to_display(meeting)
    assert result["start_th"].tzinfo == tz.gettz('Asia/Bangkok')
    assert result["start_ua"].tzinfo == tz.gettz('Europe/Kiev')
    
    # Test with custom timezones
    result = convert_meeting_to_display(meeting, ua_tz='America/New_York', th_tz='Pacific/Auckland')
    assert result["start_th"].tzinfo == tz.gettz('Pacific/Auckland')
    assert result["start_ua"].tzinfo == tz.gettz('America/New_York')

def test_filter_meetings_special_cases():
    meetings = [
        {"attendants": ["@user1", "@USER1"]},  # Case sensitivity
        {"attendants": ["@user1 ", " @user1"]}, # Whitespace
        {"attendants": ["@user1,@user2"]},      # Invalid format
    ]
    
    filtered = filter_meetings(meetings, True, "@user1")
    assert len(filtered) == 2
    
    # Test with None inputs
    assert filter_meetings(None, True, "@user1") == []
    assert filter_meetings(meetings, True, None) == []