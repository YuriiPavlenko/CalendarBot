import pytest
from datetime import datetime, timedelta, UTC
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

def test_get_today_th():
    start, end = get_today_th()
    assert end - start == timedelta(days=1)
    assert start.tzinfo == tz.gettz('Asia/Bangkok')

def test_get_tomorrow_th():
    start, end = get_tomorrow_th()
    assert end - start == timedelta(days=1)
    assert start > datetime.now(tz.gettz('Asia/Bangkok'))

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