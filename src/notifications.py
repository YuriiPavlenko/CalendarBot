import logging
from database import SessionLocal, get_user_settings
from localization import STRINGS
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def notify_users_new_meeting(meeting, user_list):
    text = STRINGS["notify_new_meeting"].format(details=formatted_meeting(meeting))
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
    users = session.execute("SELECT user_id FROM user_settings").fetchall()
    user_ids = [u[0] for u in users]
    filtered = []
    for uid in user_ids:
        us = get_user_settings(session, uid)
        if us.notify_new:
            if us.filter_type == "mine":
                if any(a == f"@{uid}" for a in meeting["attendants"]):
                    filtered.append(uid)
            else:
                filtered.append(uid)
    session.close()
    return filtered
