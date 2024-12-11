import os
from flask import Flask, request, render_template, redirect
from src.database import SessionLocal, get_user_settings, set_filter, set_notifications
from src.cache import cache
from src.utils import filter_meetings, get_today_th, get_tomorrow_th, get_rest_week_th, get_next_week_th
from sqlalchemy import text

app = Flask(__name__, template_folder='templates', static_folder='static')

def get_filtered_meetings(user_id, period):
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    session.close()
    meetings = cache.get_meetings()

    if period == "today":
        start, end = get_today_th()
    elif period == "tomorrow":
        start, end = get_tomorrow_th()
    elif period == "rest_week":
        start, end = get_rest_week_th()
    elif period == "next_week":
        start, end = get_next_week_th()
    else:
        return []

    filtered_range = [m for m in meetings if m["start_th"] >= start and m["start_th"] < end]
    filtered = filter_meetings(filtered_range, us.filter_type, f"@{user_id}")
    return filtered

@app.route("/")
def index():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return "Missing user_id", 400

    session = SessionLocal()
    us = get_user_settings(session, user_id)
    filter_type = us.filter_type
    n1h = us.notify_1h
    n15m = us.notify_15m
    n5m = us.notify_5m
    nnew = us.notify_new
    session.close()

    today_meetings = get_filtered_meetings(user_id, "today")
    tomorrow_meetings = get_filtered_meetings(user_id, "tomorrow")
    rest_week_meetings = get_filtered_meetings(user_id, "rest_week")
    next_week_meetings = get_filtered_meetings(user_id, "next_week")

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
                           next_week_meetings=next_week_meetings)

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

    return redirect(f"/?user_id={user_id}")

# No app.run() here because we use gunicorn in production.
