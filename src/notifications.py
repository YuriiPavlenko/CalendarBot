import logging
from .database import SessionLocal, get_user_settings
from .localization import STRINGS
from telegram import Bot
from .config import TELEGRAM_BOT_TOKEN
from .utils import filter_meetings
import datetime
from .config import TIMEZONE_TH
from dateutil import tz
from sqlalchemy import text

logger = logging.getLogger(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

initialized = False
previous_map = {}

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
    session = SessionLocal()
    users = session.execute(text("SELECT user_id FROM user_settings")).fetchall()
    user_ids = [u[0] for u in users]
    filtered = []
    for uid in user_ids:
        us = get_user_settings(session, uid)
        filter_type = us.filter_type
        notify_new = us.notify_new
        if notify_new:
            if filter_type == "mine":
                if any(a == f"@{uid}" or (us.username and a == us.username) for a in meeting["attendants"]):
                    filtered.append(uid)
            else:
                filtered.append(uid)
    session.close()
    return filtered

def get_subscribed_users_for_before(meeting, delta_minutes):
    session = SessionLocal()
    users = session.execute(text("SELECT user_id FROM user_settings")).fetchall()
    user_ids = [u[0] for u in users]
    filtered = []
    for uid in user_ids:
        us = get_user_settings(session, uid)
        filter_type = us.filter_type
        notify_1h = us.notify_1h
        notify_15m = us.notify_15m
        notify_5m = us.notify_5m

        notify_attr = False
        if delta_minutes == 60 and notify_1h:
            notify_attr = True
        elif delta_minutes == 15 and notify_15m:
            notify_attr = True
        elif delta_minutes == 5 and notify_5m:
            notify_attr = True
        
        if notify_attr:
            if filter_type == "mine":
                if any(a == f"@{uid}" or (us.username and a == us.username) for a in meeting["attendants"]):
                    filtered.append(uid)
            else:
                filtered.append(uid)
    session.close()
    return filtered

def check_and_send_before_notifications(meetings):
    now = datetime.datetime.now(tz.gettz(TIMEZONE_TH))
    for m in meetings:
        start = m["start_th"]
        diff = (start - now).total_seconds() / 60.0
        diff_rounded = round(diff)
        if diff_rounded in [60,15,5]:
            user_list = get_subscribed_users_for_before(m, diff_rounded)
            if user_list:
                notify_users_before_meeting(m, user_list)

def handle_new_and_updated_meetings(new_map):
    global initialized, previous_map
    if not initialized:
        # First run, just store
        previous_map = new_map
        initialized = True
        return

    # Subsequent runs
    # New meetings:
    for mid, m in new_map.items():
        if mid not in previous_map:
            # truly new meeting
            subscribers = get_subscribed_users_for_new(m)
            if subscribers:
                notify_users_new_meeting(m, subscribers)
        else:
            # check updated
            if m["updated"] != previous_map[mid].get("updated"):
                # treat updated like new meeting event if desired
                subscribers = get_subscribed_users_for_new(m)
                if subscribers:
                    notify_users_new_meeting(m, subscribers)

    previous_map = new_map
