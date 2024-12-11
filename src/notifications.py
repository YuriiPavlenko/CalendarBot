import logging
from .database import SessionLocal, get_user_settings
from .localization import STRINGS
from telegram import Bot
from .config import TELEGRAM_BOT_TOKEN, TIMEZONE_TH
from .utils import filter_meetings
import datetime
from dateutil import tz

logger = logging.getLogger(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def notify_users_new_meeting(meeting, user_list):
    text = STRINGS["notify_new_meeting"].format(details=formatted_meeting(meeting))
    for user_id in user_list:
        bot.send_message(chat_id=user_id, text=text)

def notify_users_before_meeting(meeting, user_list):
    text = STRINGS["notify_before_meeting"].format(details=formatted_meeting(meeting))
    for user_id in user_list:
        bot.send_message(chat_id=user_id, text=text)

def formatted_meeting(m):
    desc = m["description"] if m["description"] else ""
    loc = m["location"] if m["location"] else ""
    link = m["hangoutLink"] if m["hangoutLink"] else ""
    attendants_str = ", ".join(m["attendants"]) if m["attendants"] else ""
    return STRINGS["meeting_details"].format(
        title=m["title"],
        start_ua=m["start_ua"].strftime("%Y-%m-%d %H:%M"),
        start_th=m["start_th"].strftime("%Y-%m-%d %H:%M"),
        end_ua=m["end_ua"].strftime("%Y-%m-%d %H:%M"),
        end_th=m["end_th"].strftime("%Y-%m-%d %H:%M"),
        attendants=attendants_str,
        location=loc,
        link=link,
        desc=desc
    )

def get_subscribed_users_for_new(meeting):
    from sqlalchemy import text
    session = SessionLocal()
    users = session.execute(text("SELECT user_id FROM user_settings")).fetchall()
    user_ids = [u[0] for u in users]
    filtered = []
    for uid in user_ids:
        us = get_user_settings(session, uid)
        # Extract attributes
        notify_new = us.notify_new
        filter_type = us.filter_type
        if notify_new:
            if filter_type == "mine":
                if any(a == f"@{uid}" for a in meeting["attendants"]):
                    filtered.append(uid)
            else:
                filtered.append(uid)
    session.close()
    return filtered


def get_subscribed_users_for_before(meeting, delta_minutes):
    from sqlalchemy import text
    session = SessionLocal()
    users = session.execute(text("SELECT user_id FROM user_settings")).fetchall()
    user_ids = [u[0] for u in users]
    filtered = []
    for uid in user_ids:
        us = get_user_settings(session, uid)
        notify_1h = us.notify_1h
        notify_15m = us.notify_15m
        notify_5m = us.notify_5m
        filter_type = us.filter_type

        notify_attr = False
        if delta_minutes == 60 and notify_1h:
            notify_attr = True
        elif delta_minutes == 15 and notify_15m:
            notify_attr = True
        elif delta_minutes == 5 and notify_5m:
            notify_attr = True
        
        if notify_attr:
            if filter_type == "mine":
                if any(a == f"@{uid}" for a in meeting["attendants"]):
                    filtered.append(uid)
            else:
                filtered.append(uid)
    session.close()
    return filtered

def check_and_send_before_notifications(meetings):
    # Called every minute. If a meeting starts in exactly 60 min, 15 min or 5 min, send notification.
    now = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    for m in meetings:
        start = m["start_th"]
        diff = (start - now).total_seconds() / 60.0
        diff_rounded = round(diff)
        # If diff_rounded == 60 or == 15 or == 5 send notifications
        if diff_rounded in [60,15,5]:
            user_list = get_subscribed_users_for_before(m, diff_rounded)
            notify_users_before_meeting(m, user_list)
