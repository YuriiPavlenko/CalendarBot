import pytest
from datetime import datetime, timedelta
from dateutil import tz
from src.formatters import (
    format_meeting_time,
    formatted_meeting,
    format_meetings_list
)
from src.localization import STRINGS

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

def test_format_meetings_list_empty():
    meetings = []
    result = format_meetings_list(meetings)
    assert result == STRINGS["no_meetings"]

def test_format_meetings_list_missing_fields():
    meetings = [{
        "title": "Meeting with missing fields",
        "start_th": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Asia/Bangkok')),
        "end_th": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Asia/Bangkok')),
        "start_ua": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Europe/Kiev')),
        "end_ua": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Europe/Kiev')),
    }]
    result = format_meetings_list(meetings)
    assert "Meeting with missing fields" in result

def test_format_meetings_list_empty_attendants():
    meetings = [{
        "title": "Meeting with empty attendants",
        "start_th": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Asia/Bangkok')),
        "end_th": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Asia/Bangkok')),
        "start_ua": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Europe/Kiev')),
        "end_ua": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Europe/Kiev')),
        "attendants": []
    }]
    result = format_meetings_list(meetings)
    assert "Meeting with empty attendants" in result
    assert "Участники" not in result

def test_format_meetings_list_special_characters():
    meetings = [{
        "title": "Meeting with special characters: !@#$%^&*()",
        "start_th": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Asia/Bangkok')),
        "end_th": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Asia/Bangkok')),
        "start_ua": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Europe/Kiev')),
        "end_ua": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Europe/Kiev')),
        "description": "Description with special characters: !@#$%^&*()"
    }]
    result = format_meetings_list(meetings)
    assert "Meeting with special characters: !@#$%^&*()" in result
    assert "Description with special characters: !@#$%^&*()" in result

def test_format_meetings_list_multiple_days():
    meetings = [
        {
            "title": "Meeting Day 1",
            "start_th": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Asia/Bangkok')),
            "end_th": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Asia/Bangkok')),
            "start_ua": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Europe/Kiev')),
            "end_ua": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Europe/Kiev')),
        },
        {
            "title": "Meeting Day 2",
            "start_th": datetime(2024, 12, 18, 15, 0, tzinfo=tz.gettz('Asia/Bangkok')),
            "end_th": datetime(2024, 12, 18, 16, 0, tzinfo=tz.gettz('Asia/Bangkok')),
            "start_ua": datetime(2024, 12, 18, 15, 0, tzinfo=tz.gettz('Europe/Kiev')),
            "end_ua": datetime(2024, 12, 18, 16, 0, tzinfo=tz.gettz('Europe/Kiev')),
        }
    ]
    result = format_meetings_list(meetings)
    assert "Meeting Day 1" in result
    assert "Meeting Day 2" in result

def test_format_meetings_list_overlapping_times():
    meetings = [
        {
            "title": "Meeting 1",
            "start_th": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Asia/Bangkok')),
            "end_th": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Asia/Bangkok')),
            "start_ua": datetime(2024, 12, 17, 15, 0, tzinfo=tz.gettz('Europe/Kiev')),
            "end_ua": datetime(2024, 12, 17, 16, 0, tzinfo=tz.gettz('Europe/Kiev')),
        },
        {
            "title": "Meeting 2",
            "start_th": datetime(2024, 12, 17, 15, 30, tzinfo=tz.gettz('Asia/Bangkok')),
            "end_th": datetime(2024, 12, 17, 16, 30, tzinfo=tz.gettz('Asia/Bangkok')),
            "start_ua": datetime(2024, 12, 17, 15, 30, tzinfo=tz.gettz('Europe/Kiev')),
            "end_ua": datetime(2024, 12, 17, 16, 30, tzinfo=tz.gettz('Europe/Kiev')),
        }
    ]
    result = format_meetings_list(meetings)
    assert "Meeting 1" in result
    assert "Meeting 2" in result