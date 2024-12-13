import pytest
from datetime import datetime, timedelta
from dateutil import tz
from src.formatters import (
    format_meeting_time,
    formatted_meeting,
    format_meetings_list
)

@pytest.fixture
def sample_meeting():
    return {
        "title": "Test Meeting",
        "start_th": datetime.now(tz.gettz('Asia/Bangkok')),
        "end_th": datetime.now(tz.gettz('Asia/Bangkok')) + timedelta(hours=1),
        "start_ua": datetime.now(tz.gettz('Europe/Kiev')),
        "end_ua": datetime.now(tz.gettz('Europe/Kiev')) + timedelta(hours=1),
        "attendants": ["@user1", "@user2"],
        "location": "Room 1",
        "hangoutLink": "https://meet.google.com/123",
        "description": "Test description"
    }

def test_format_meeting_time(sample_meeting):
    result = format_meeting_time(sample_meeting)
    assert isinstance(result, str)
    assert ":" in result  # Should contain time
    assert "." in result  # Should contain date

def test_formatted_meeting(sample_meeting):
    result = formatted_meeting(sample_meeting)
    assert sample_meeting["title"] in result
    assert "Таиланд:" in result
    assert "Украина:" in result