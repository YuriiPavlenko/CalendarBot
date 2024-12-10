from apscheduler.schedulers.background import BackgroundScheduler
import logging
import datetime
from dateutil import tz
from src.google_calendar import fetch_meetings
from src.database import SessionLocal, get_user_settings
from src.utils import format_meeting

# We'll run periodic checks to find meetings and schedule notifications.
# This is a simplistic approach. In production, you'd store scheduled jobs in a DB.

scheduler = BackgroundScheduler()

# This function should be called periodically (e.g. every 5 or 10 min) to schedule notifications
def schedule_meeting_notifications(bot):
    # For simplicity, fetch upcoming meetings for the next day and schedule them
    # This could be optimized.
    now = datetime.datetime.utcnow().replace(tzinfo=tz.UTC)
    future = now + datetime.timedelta(days=1)
    meetings = fetch_meetings(now, future)

    session = SessionLocal()
    # For each user, schedule notifications if needed
    users = session.execute("SELECT user_id FROM user_settings").fetchall()
    for (user_id,) in users:
        settings = get_user_settings(session, user_id)
        user_nickname = f"@{user_id}" # This is a simplification. In reality, you'd map user_id to nickname.
                                      # Since we don't have user-nickname mapping from Telegram explicitly,
                                      # you would handle it when user starts (/start) and store their nickname.

        # Filter meetings if needed is done when sending notifications
        for m in meetings:
            if settings.filter_type == "mine" and user_nickname not in m["attendants"]:
                continue
            # If notifications enabled, schedule them
            if settings.notify_1h:
                t = m["start_th"] - datetime.timedelta(hours=1)
                if t > datetime.datetime.now(t.tzinfo):
                    scheduler.add_job(send_notification, 'date', run_date=t, args=[bot, user_id, m])
            if settings.notify_15m:
                t = m["start_th"] - datetime.timedelta(minutes=15)
                if t > datetime.datetime.now(t.tzinfo):
                    scheduler.add_job(send_notification, 'date', run_date=t, args=[bot, user_id, m])
            if settings.notify_5m:
                t = m["start_th"] - datetime.timedelta(minutes=5)
                if t > datetime.datetime.now(t.tzinfo):
                    scheduler.add_job(send_notification, 'date', run_date=t, args=[bot, user_id, m])

    session.close()

def send_notification(bot, user_id, meeting):
    from src.localization import STRINGS
    text = STRINGS["notify_before_meeting"].format(details=format_meeting(meeting))
    bot.send_message(chat_id=user_id, text=text)

def notify_new_meeting(bot, meeting):
    # Called when a new meeting is added
    from src.localization import STRINGS
    session = SessionLocal()
    users = session.execute("SELECT user_id FROM user_settings").fetchall()
    for (user_id,) in users:
        settings = get_user_settings(session, user_id)
        user_nickname = f"@{user_id}"
        if settings.notify_new:
            if settings.filter_type == "mine":
                if user_nickname in meeting["attendants"]:
                    bot.send_message(chat_id=user_id, text=STRINGS["notify_new_meeting"].format(details=format_meeting(meeting)))
            else:
                bot.send_message(chat_id=user_id, text=STRINGS["notify_new_meeting"].format(details=format_meeting(meeting)))
    session.close()
