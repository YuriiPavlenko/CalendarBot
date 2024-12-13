import pytest
from datetime import datetime, timedelta
from dateutil import tz
from src.database import Meeting
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
        {"attendants": ["@user1", "@user2"]},
        {"attendants": ["@user3"]},
        {"attendants": ["@user1"]}
    ]

def test_filter_meetings(sample_meetings):
    filtered = filter_meetings(sample_meetings, True, "@user1")
    assert len(filtered) == 2
    assert all("@user1" in m["attendants"] for m in filtered)

def test_get_today_th():
    start, end = get_today_th()
    assert end - start == timedelta(days=1)
    assert start.tzinfo == tz.gettz('Asia/Bangkok')

def test_get_tomorrow_th():
    start, end = get_tomorrow_th()
    assert end - start == timedelta(days=1)
    assert start > datetime.now(tz.gettz('Asia/Bangkok'))

def test_convert_meeting_to_display():
    meeting = Meeting(
        id="123",
        title="Test",
        start_time=datetime.now(tz.UTC),
        end_time=datetime.now(tz.UTC) + timedelta(hours=1),
        attendants="@user1,@user2",
        location="Room 1"
    )
    
    result = convert_meeting_to_display(meeting)
    assert result["id"] == "123"
    assert "start_ua" in result
    assert "start_th" in result
    assert isinstance(result["attendants"], list)