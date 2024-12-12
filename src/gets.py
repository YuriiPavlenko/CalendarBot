from dateutil import tz
from .utils import convert_meeting_to_display
# ...existing imports...

def get_meetings_for_today():
    th_tz = tz.gettz(TIMEZONE_TH)
    now_th = datetime.datetime.now(th_tz)
    start_th = now_th.replace(hour=0, minute=0, second=0, microsecond=0)
    end_th = start_th + datetime.timedelta(days=1)
    
    # Convert to UTC for database query
    start_utc = start_th.astimezone(tz.UTC)
    end_utc = end_th.astimezone(tz.UTC)
    
    session = SessionLocal()
    try:
        meetings = session.query(Meeting).filter(
            Meeting.start_time >= start_utc,
            Meeting.start_time < end_utc
        ).all()
        return [convert_meeting_to_display(m) for m in meetings]
    finally:
        session.close()

# Similarly update other meeting fetching functions...
# ...existing code...
