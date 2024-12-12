from flask import Flask, request, render_template, redirect, url_for
from src.database import SessionLocal, get_user_settings, set_filter, set_notifications, Meeting
from src.utils import get_end_of_next_week
from datetime import datetime, timedelta
import pytz

app = Flask(__name__, template_folder='templates', static_folder='static')

def get_meetings(user_id):
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    show_only_mine = us.filter_by_attendant
    user_identifier = us.username if us.username else f"@{user_id}"
    
    # Use start of today instead of now
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_next_week = get_end_of_next_week()
    
    meetings_query = session.query(Meeting).filter(
        Meeting.start_th >= today,
        Meeting.start_th <= end_next_week
    )
    if show_only_mine:
        meetings_query = meetings_query.filter(Meeting.attendants.contains(user_identifier))
    meetings = meetings_query.all()
    session.close()
    return meetings

def get_day_name(date):
    days = {
        0: 'Понедельник',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье'
    }
    if date.date() == datetime.now().date():
        return "Сегодня"
    if date.date() == (datetime.now() + timedelta(days=1)).date():
        return "Завтра"
    return days[date.weekday()]

def group_meetings_by_days(meetings):
    # Start from today and get all weekdays until next week's Friday
    today = datetime.now().date()
    dates = []
    current = today
    
    # Calculate the target end date (next week's Friday)
    days_until_friday = (4 - today.weekday()) % 7  # Days until this week's Friday
    if days_until_friday == 0:
        days_until_friday = 7  # Go to next Friday
    target_end = today + timedelta(days=days_until_friday + 7)  # Add another week
    
    while current <= target_end:
        if current.weekday() <= 4:  # Only weekdays (Monday-Friday)
            dates.append(current)
        current += timedelta(days=1)

    # ...existing code for grouping meetings...
    grouped_meetings = []
    for date in dates:
        day_meetings = [m for m in meetings if m.start_th.date() == date]
        grouped_meetings.append({
            'date': date,
            'day_name': get_day_name(datetime.combine(date, datetime.min.time())),
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
                        'title': m.title,
                        'start_ua': m.start_ua.strftime("%H:%M"),
                        'end_ua': m.end_ua.strftime("%H:%M"),
                        'start_th': m.start_th.strftime("%H:%M"),
                        'end_th': m.end_th.strftime("%H:%M"),
                        'attendants': m.attendants,
                        'location': m.location,
                        'hangoutLink': m.hangoutLink,
                        'description': m.description
                    } for m in day['meetings']
                ]
            } for day in grouped_meetings
        ]
    }
