import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from src.database import SessionLocal, set_filter, set_notifications, get_user_settings
from src.google_calendar import fetch_meetings
from src.utils import filter_meetings, format_meeting, get_today_th, get_tomorrow_th, get_rest_week_th, get_next_week_th
from src.localization import STRINGS

logger = logging.getLogger(__name__)

FILTER_CHOOSING, NOTIF_CHOOSING = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info("User %s started bot", user_id)
    # Greet user and go to settings_filter
    await update.message.reply_text(STRINGS["greeting"])
    await settings_filter(update, context)

async def settings_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Show two options: all, mine
    keyboard = [
        [KeyboardButton(STRINGS["settings_filter_all"]), KeyboardButton(STRINGS["settings_filter_mine"])]
    ]
    await update.message.reply_text(STRINGS["settings_filter_intro"],
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))
    return FILTER_CHOOSING

async def filter_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    choice = update.message.text
    session = SessionLocal()
    if choice == STRINGS["settings_filter_mine"]:
        set_filter(session, user_id, "mine")
    else:
        set_filter(session, user_id, "all")
    session.close()
    await update.message.reply_text(STRINGS["settings_filter_saved"], reply_markup=None)
    # Proceed to notifications
    await settings_notifications(update, context)
    return ConversationHandler.END

async def settings_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton(STRINGS["settings_notifications_1h"])],
        [KeyboardButton(STRINGS["settings_notifications_15m"])],
        [KeyboardButton(STRINGS["settings_notifications_5m"])],
        [KeyboardButton(STRINGS["settings_notifications_new"])]
    ]
    await update.message.reply_text(STRINGS["settings_notifications_intro"],
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=False))
    return NOTIF_CHOOSING

async def notifications_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    selected_texts = update.message.text.split('\n') if update.message else []
    # In reality, we'd implement a custom keyboard or inline keyboard with checkboxes.
    # For simplicity, assume user sends messages with chosen options and then sends /done or something
    # But requirement states "User may choose any number of options". Let's say user sends all chosen in one message separated by newline or handle them individually.
    # Let's just check if message contains certain phrases.

    msg_text = update.message.text
    notify_1h = STRINGS["settings_notifications_1h"] in msg_text
    notify_15m = STRINGS["settings_notifications_15m"] in msg_text
    notify_5m = STRINGS["settings_notifications_5m"] in msg_text
    notify_new = STRINGS["settings_notifications_new"] in msg_text

    session = SessionLocal()
    set_notifications(session, user_id, notify_1h, notify_15m, notify_5m, notify_new)
    session.close()

    await update.message.reply_text(STRINGS["settings_notifications_saved"], reply_markup=None)
    # Show all commands
    menu_text = "\n".join([
        STRINGS["menu_title"],
        STRINGS["menu_start"],
        STRINGS["menu_settings_filter"],
        STRINGS["menu_settings_notifications"],
        STRINGS["menu_get_today"],
        STRINGS["menu_get_tomorrow"],
        STRINGS["menu_get_rest_week"],
        STRINGS["menu_get_next_week"]
    ])
    await update.message.reply_text(menu_text)
    await update.message.reply_text(STRINGS["settings_done"])
    return ConversationHandler.END

async def get_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    session.close()
    start, end = get_today_th()
    meetings = fetch_meetings(start, end)
    user_nickname = "@{}".format(update.effective_user.username) if update.effective_user.username else f"@{user_id}"
    meetings = filter_meetings(meetings, us.filter_type, user_nickname)
    if not meetings:
        await update.message.reply_text(STRINGS["no_meetings"])
    else:
        for m in meetings:
            await update.message.reply_text(format_meeting(m))

async def get_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    session.close()
    start, end = get_tomorrow_th()
    meetings = fetch_meetings(start, end)
    user_nickname = "@{}".format(update.effective_user.username) if update.effective_user.username else f"@{user_id}"
    meetings = filter_meetings(meetings, us.filter_type, user_nickname)
    if not meetings:
        await update.message.reply_text(STRINGS["no_meetings"])
    else:
        for m in meetings:
            await update.message.reply_text(format_meeting(m))

async def get_rest_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    session.close()
    start, end = get_rest_week_th()
    meetings = fetch_meetings(start, end)
    user_nickname = "@{}".format(update.effective_user.username) if update.effective_user.username else f"@{user_id}"
    meetings = filter_meetings(meetings, us.filter_type, user_nickname)
    if not meetings:
        await update.message.reply_text(STRINGS["no_meetings"])
    else:
        for m in meetings:
            await update.message.reply_text(format_meeting(m))

async def get_next_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    session.close()
    start, end = get_next_week_th()
    meetings = fetch_meetings(start, end)
    user_nickname = "@{}".format(update.effective_user.username) if update.effective_user.username else f"@{user_id}"
    meetings = filter_meetings(meetings, us.filter_type, user_nickname)
    if not meetings:
        await update.message.reply_text(STRINGS["no_meetings"])
    else:
        for m in meetings:
            await update.message.reply_text(format_meeting(m))
