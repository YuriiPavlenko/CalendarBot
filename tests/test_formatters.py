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
        "title": "Штурм иконок",
        "start_th": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Asia/Bangkok')),
        "end_th": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Asia/Bangkok')),
        "start_ua": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Europe/Kiev')),
        "end_ua": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Europe/Kiev')),
        "attendants": ["@ohshtein", "@romann_92", "@koshkooo", "@emerel", "@barslav", "@hmerijes"],
        "hangoutLink": "https://meet.google.com/etc-wqwm-ege",
        "description": ""
    }

def test_format_meeting_time(sample_meeting):
    result = format_meeting_time(sample_meeting)
    assert isinstance(result, str)
    assert ":" in result  # Should contain time
    assert "." in result  # Should contain date

def test_formatted_meeting(sample_meeting):
    result = formatted_meeting(sample_meeting)
    assert "Штурм иконок" in result
    assert "Таиланд:" in result
    assert "Украина:" in result
    assert "https://meet.google.com/etc-wqwm-ege" in result
    assert "@ohshtein" in result
    assert "@romann_92" in result
    assert "15:00" in result  # Check for specific time
    assert "16:00" in result  # Check for end time

def test_format_meetings_list():
    meetings = [{
        "title": "Штурм иконок",
        "start_th": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Asia/Bangkok')),
        "end_th": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Asia/Bangkok')),
        "start_ua": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Europe/Kiev')),
        "end_ua": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Europe/Kiev')),
        "attendants": ["@ohshtein", "@romann_92"],
        "hangoutLink": "https://meet.google.com/etc-wqwm-ege"
    }]
    
    result = format_meetings_list(meetings)
    assert "Штурм иконок" in result
    assert "15:00" in result
    assert "16:00" in result
    assert "@ohshtein" in result
    assert "https://meet.google.com/etc-wqwm-ege" in result