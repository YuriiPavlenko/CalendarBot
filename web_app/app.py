from flask import Flask, request, render_template, redirect, url_for
from database import SessionLocal, get_user_settings, set_filter, set_notifications, Meeting
from utils import get_end_of_next_week
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')

def get_meetings(user_id):
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    filter_type = us.filter_by_attendant
    user_identifier = us.username if us.username else f"@{user_id}"
    now = datetime.now()
    end_next_week = get_end_of_next_week()
    meetings_query = session.query(Meeting).filter(Meeting.start_th >= now, Meeting.start_th <= end_next_week)
    if filter_type == "mine":
        meetings_query = meetings_query.filter(Meeting.attendants.contains(user_identifier))
    meetings = meetings_query.all()
    session.close()
    return meetings

@app.route("/")
def index():
    user_id = request.args.get("user_id", type=int)
    settings_saved = request.args.get("saved", default=False, type=bool)
    if not user_id:
        return "Missing user_id", 400

    session = SessionLocal()
    us = get_user_settings(session, user_id)
    filter_type = us.filter_by_attendant
    n1h = us.notify_1h
    n15m = us.notify_15m
    n5m = us.notify_5m
    nnew = us.notify_new
    session.close()

    today_meetings = get_filtered_meetings(user_id, "today")
    tomorrow_meetings = get_filtered_meetings(user_id, "tomorrow")
    rest_week_meetings = get_filtered_meetings(user_id, "rest_week")
    next_week_meetings = get_filtered_meetings(user_id, "next_week")
    meetings = get_meetings(user_id)

    return render_template("index.html",
                           user_id=user_id,
                           filter_type=filter_type,
                           notify_1h=n1h,
                           notify_15m=n15m,
                           notify_5m=n5m,
                           notify_new=nnew,
                           today_meetings=today_meetings,
                           tomorrow_meetings=tomorrow_meetings,
                           rest_week_meetings=rest_week_meetings,
                           next_week_meetings=next_week_meetings,
                           meetings=meetings,
                           settings_saved=settings_saved)

@app.route("/save", methods=["POST"])
def save_settings():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return "Missing user_id", 400

    filter_type = request.form.get("filter_type","all")
    notify_1h = "notify_1h" in request.form
    notify_15m = "notify_15m" in request.form
    notify_5m = "notify_5m" in request.form
    notify_new = "notify_new" in request.form

    session = SessionLocal()
    set_filter(session, user_id, filter_type)
    set_notifications(session, user_id, notify_1h, notify_15m, notify_5m, notify_new)
    session.close()

    return redirect(url_for('index', user_id=user_id, saved=True))
