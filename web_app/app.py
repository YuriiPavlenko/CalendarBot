import os
from flask import Flask, request, render_template, redirect
from src.database import SessionLocal, get_user_settings, set_filter, set_notifications
from src.cache import cache
from src.utils import filter_meetings

app = Flask(__name__, template_folder='templates', static_folder='static')

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

    meetings = cache.get_meetings()
    filtered = filter_meetings(meetings, filter_type, f"@{user_id}")

    # Group by date
    by_day = {}
    for m in filtered:
        d = m["start_th"].strftime("%Y-%m-%d")
        if d not in by_day:
            by_day[d] = []
        by_day[d].append(m)

    return render_template("index.html",
                           filter_type=filter_type,
                           notify_1h=n1h,
                           notify_15m=n15m,
                           notify_5m=n5m,
                           notify_new=nnew,
                           meetings=by_day)


@app.route("/save", methods=["POST"])
def save():
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

if __name__ == "__main__":
    # Run flask on a port behind a reverse proxy or your chosen host setup
    app.run(host="0.0.0.0", port=8080)
