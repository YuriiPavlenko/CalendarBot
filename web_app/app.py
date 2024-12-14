from flask import Flask, request, render_template, redirect, url_for, jsonify
from database import SessionLocal, get_user_settings, set_filter, set_notifications, Meeting
from src.utils import get_end_of_next_week, convert_meeting_to_display
from src.config import TIMEZONE_TH  # Add this import
from datetime import datetime, timedelta
from dateutil import tz

app = Flask(__name__, template_folder='templates', static_folder='static')

def get_meetings(user_id):
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    show_only_mine = us.filter_by_attendant
    user_identifier = us.username if us.username else f"@{user_id}"
    
    # Convert today to UTC for database query
    today = datetime.now(tz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    end_next_week = get_end_of_next_week().astimezone(tz.UTC)
    
    meetings_query = session.query(Meeting).filter(
        Meeting.start_time >= today,
        Meeting.start_time <= end_next_week
    )
    if show_only_mine:
        meetings_query = meetings_query.filter(Meeting.attendants.contains(user_identifier))
    meetings = meetings_query.all()
    
    # Convert meetings to display format with proper timezones
    formatted_meetings = [convert_meeting_to_display(m) for m in meetings]
    session.close()
    return formatted_meetings

def get_day_name(date, th_tz=tz.gettz(TIMEZONE_TH)):
    """Get localized day name, comparing with Thai timezone's today."""
    days = {
        0: 'Понедельник',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье'
    }
    
    # Get current date in Thai timezone
    now_th = datetime.now(th_tz).date()
    
    if date == now_th:
        return "Сегодня"
    if date == (now_th + timedelta(days=1)):
        return "Завтра"
    return days[date.weekday()]

def group_meetings_by_days(meetings):
    """Group meetings by their Thai timezone dates."""
    th_tz = tz.gettz(TIMEZONE_TH)
    
    # Get today in Thai timezone
    today_th = datetime.now(th_tz).date()
    
    # Calculate dates range
    dates = []
    current = today_th
    weekday = today_th.weekday()
    
    # Calculate end of next week (next week's Friday)
    days_until_next_friday = ((4 - weekday) + 7) % 7  # Days until next Friday
    if days_until_next_friday == 0:
        days_until_next_friday = 7  # If today is Friday, go to next Friday
    end_date = today_th + timedelta(days=days_until_next_friday)
    
    
    # Collect all weekdays until end date
    while current <= end_date:
        if current.weekday() <= 4:  # Only weekdays
            dates.append(current)
        current += timedelta(days=1)
    
    # Group meetings by their Thai timezone date
    grouped_meetings = []
    for date in dates:
        day_meetings = [
            m for m in meetings 
            if m["start_th"].astimezone(th_tz).date() == date
        ]
        
        grouped_meetings.append({
            'date': date,
            'day_name': get_day_name(date, th_tz),
            'meetings': day_meetings
        })
    
    return grouped_meetings

@app.route("/")
def index():
    user_id = request.args.get("user_id", type=int)
    settings_saved = request.args.get("saved", default=False, type=bool)
    if not user_id:
        return "Missing user_id", 400

    session = SessionLocal()
    us = get_user_settings(session, user_id)
    show_only_mine = us.filter_by_attendant
    n1h = us.notify_1h
    n15m = us.notify_15m
    n5m = us.notify_5m
    nnew = us.notify_new
    session.close()

    meetings = get_meetings(user_id)
    grouped_meetings = group_meetings_by_days(meetings)

    return render_template("index.html",
                           user_id=user_id,
                           show_only_mine=show_only_mine,
                           notify_1h=n1h,
                           notify_15m=n15m,
                           notify_5m=n5m,
                           notify_new=nnew,
                           grouped_meetings=grouped_meetings,
                           settings_saved=settings_saved)

@app.route("/save", methods=["POST"])
def save_settings():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return "Missing user_id", 400

    show_only_mine = request.form.get("show_only_mine") == "true"
    notify_1h = "notify_1h" in request.form
    notify_15m = "notify_15m" in request.form
    notify_5m = "notify_5m" in request.form
    notify_new = "notify_new" in request.form

    session = SessionLocal()
    set_filter(session, user_id, show_only_mine)
    set_notifications(session, user_id, notify_1h, notify_15m, notify_5m, notify_new)
    session.close()

    return redirect(url_for('index', user_id=user_id, saved=True))

@app.route("/meetings")
def get_meetings_json():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return "Missing user_id", 400

    meetings = get_meetings(user_id)
    grouped_meetings = group_meetings_by_days(meetings)
    
    return {
        'meetings': [
            {
                'date': day['date'].strftime('%Y-%m-%d'),
                'day_name': day['day_name'],
                'meetings': [
                    {
                        'title': m["title"],
                        'start_ua': m["start_ua"].strftime("%H:%M"),
                        'end_ua': m["end_ua"].strftime("%H:%M"),
                        'start_th': m["start_th"].strftime("%H:%M"),
                        'end_th': m["end_th"].strftime("%H:%M"),
                        'attendants': m["attendants"],
                        'location': m["location"],
                        'hangoutLink': m["hangoutLink"],
                        'description': m["description"]
                    } for m in day['meetings']
                ]
            } for day in grouped_meetings
        ]
    }

@app.route("/api/meetings/")
def get_meetings_api():
    # Get start and end from query parameters
    try:
        start_str = request.args.get('start')
        end_str = request.args.get('end')
        
        if start_str:
            start = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        else:
            start = datetime.now(tz.UTC)
            
        if end_str:
            end = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
        else:
            end = start + timedelta(days=7)
        
        # Ensure times are UTC
        if start.tzinfo is None:
            start = start.replace(tzinfo=tz.UTC)
        if end.tzinfo is None:
            end = end.replace(tzinfo=tz.UTC)
        
        session = SessionLocal()
        try:
            meetings = session.query(Meeting).filter(
                Meeting.start_time >= start,
                Meeting.start_time < end
            ).all()
            return jsonify([convert_meeting_to_display(m) for m in meetings])
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ...rest of the code...
