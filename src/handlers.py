import logging
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
)
from database import SessionLocal, set_filter, set_notifications, get_user_settings
from google_calendar import fetch_meetings
from localization import STRINGS
from utils import filter_meetings, format_meetings_list

logger = logging.getLogger(__name__)

# States for conversations
FILTER_CHOICE = 1
NOTIF_1H = 2
NOTIF_15M = 3
NOTIF_5M = 4
NOTIF_NEW = 5

FILTER_ONLY = 10  # separate conversation for /settings_filter
NOTIF_FIRST = 20  # separate conversation for /settings_notifications


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When user triggers /start:
    1) Greet the user.
    2) Ask for filter preference (all or mine) via inline keyboard.
    After user chooses, save and then automatically move to notifications.
    """
    user_id = update.effective_user.id
    logger.info("User %s started bot", user_id)
    # Greet user
    await update.message.reply_text(STRINGS["greeting"])
    # Show filter options inline
    keyboard = [
        [InlineKeyboardButton(STRINGS["settings_filter_all"], callback_data="all"),
         InlineKeyboardButton(STRINGS["settings_filter_mine"], callback_data="mine")]
    ]
    await update.message.reply_text(STRINGS["settings_filter_intro"],
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    # Mark that this conversation also should proceed to notifications after filter
    context.user_data["from_start"] = True
    return FILTER_CHOICE


async def filter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the user's filter choice in both /start and /settings_filter flows."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    choice = query.data  # "all" or "mine"
    session = SessionLocal()
    set_filter(session, user_id, choice)
    session.close()
    await query.edit_message_text(text=STRINGS["settings_filter_saved"])

    # If we're in the /start conversation, proceed to notifications
    # If it was a separate /settings_filter, just end
    if context.user_data.get("from_start", False):
        # Proceed to ask notifications
        context.user_data["from_start"] = True
        return await ask_notification_1h(query.message, context)
    else:
        # separate command: just remind that they can change later
        await query.message.reply_text("Фильтр сохранен. Вы можете изменить его позже командой /settings_filter.")
        return ConversationHandler.END


async def ask_notification_1h(message, context: ContextTypes.DEFAULT_TYPE):
    """Ask user if they want 1h notifications."""
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="yes"), InlineKeyboardButton("Нет", callback_data="no")]
    ]
    await message.reply_text(STRINGS["settings_notifications_intro"] + "\n" + STRINGS["settings_notifications_1h"],
                             reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_1H


async def notif_1h_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the user choice for 1h notifications."""
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data["notify_1h"] = (choice == "yes")
    # Now ask about 15m
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="yes"), InlineKeyboardButton("Нет", callback_data="no")]
    ]
    await query.edit_message_text(text=STRINGS["settings_notifications_15m"], reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_15M


async def notif_15m_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 15m notifications choice."""
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data["notify_15m"] = (choice == "yes")
    # Ask about 5m
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="yes"), InlineKeyboardButton("Нет", callback_data="no")]
    ]
    await query.edit_message_text(text=STRINGS["settings_notifications_5m"], reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_5M


async def notif_5m_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle 5m notifications choice."""
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data["notify_5m"] = (choice == "yes")
    # Ask about new meeting
    keyboard = [
        [InlineKeyboardButton("Да", callback_data="yes"), InlineKeyboardButton("Нет", callback_data="no")]
    ]
    await query.edit_message_text(text=STRINGS["settings_notifications_new"], reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_NEW


async def notif_new_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new meeting notifications choice."""
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data["notify_new"] = (choice == "yes")

    # Save settings to DB
    user_id = query.from_user.id
    session = SessionLocal()
    set_notifications(session, user_id,
                      context.user_data["notify_1h"],
                      context.user_data["notify_15m"],
                      context.user_data["notify_5m"],
                      context.user_data["notify_new"])
    session.close()

    await query.edit_message_text(text=STRINGS["settings_notifications_saved"])

    # If we came from start, show commands menu and done message
    if context.user_data.get("from_start", False):
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
        await query.message.reply_text(menu_text)
        await query.message.reply_text(STRINGS["settings_done"])
        context.user_data["from_start"] = False

    return ConversationHandler.END


# Separate command: /settings_filter
async def settings_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(STRINGS["settings_filter_all"], callback_data="all"),
         InlineKeyboardButton(STRINGS["settings_filter_mine"], callback_data="mine")]
    ]
    await update.message.reply_text(STRINGS["settings_filter_intro"],
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    context.user_data["from_start"] = False
    return FILTER_ONLY


async def settings_filter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Reuse the same callback from above
    return await filter_callback(update, context)


# Separate command: /settings_notifications
async def settings_notifications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Same as start's notification process, but standalone."""
    # Start by asking about 1h
    context.user_data["from_start"] = False
    return await ask_notification_1h(update.message, context)


# The same callbacks for notifications as above but used by the separate command as well
# We don't need separate functions, just reuse the same notif_x_callback.


# GET COMMANDS
# Now produce a single message with all meetings

async def get_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = f"@{update.effective_user.username}" if update.effective_user.username else f"@{user_id}"
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    session.close()

    from utils import get_today_th
    start, end = get_today_th()
    meetings = fetch_meetings(start, end)
    meetings = filter_meetings(meetings, us.filter_type, username)

    if meetings:
        text = format_meetings_list(meetings, period="today")
    else:
        text = STRINGS["no_meetings"]
    await update.message.reply_text(text, parse_mode='Markdown')


async def get_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = f"@{update.effective_user.username}" if update.effective_user.username else f"@{user_id}"
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    session.close()

    from utils import get_tomorrow_th
    start, end = get_tomorrow_th()
    meetings = fetch_meetings(start, end)
    meetings = filter_meetings(meetings, us.filter_type, username)
    if meetings:
        text = format_meetings_list(meetings, period="today")  # Just say "today" logic but we can adapt "tomorrow"
        # Let's adapt: pass period="tomorrow" to get correct heading
        text = format_meetings_list(meetings, period="tomorrow")
    else:
        text = STRINGS["no_meetings"]
    await update.message.reply_text(text, parse_mode='Markdown')


async def get_rest_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = f"@{update.effective_user.username}" if update.effective_user.username else f"@{user_id}"
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    session.close()

    from utils import get_rest_week_th
    start, end = get_rest_week_th()
    meetings = fetch_meetings(start, end)
    meetings = filter_meetings(meetings, us.filter_type, username)
    if meetings:
        text = format_meetings_list(meetings, period="week")
    else:
        text = STRINGS["no_meetings"]
    await update.message.reply_text(text, parse_mode='Markdown')


async def get_next_week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = f"@{update.effective_user.username}" if update.effective_user.username else f"@{user_id}"
    session = SessionLocal()
    us = get_user_settings(session, user_id)
    session.close()

    from utils import get_next_week_th
    start, end = get_next_week_th()
    meetings = fetch_meetings(start, end)
    meetings = filter_meetings(meetings, us.filter_type, username)
    if meetings:
        text = format_meetings_list(meetings, period="week")
    else:
        text = STRINGS["no_meetings"]
    await update.message.reply_text(text, parse_mode='Markdown')


# Define conversation handlers
filter_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("settings_filter", settings_filter)],
    states={
        FILTER_ONLY: [CallbackQueryHandler(settings_filter_callback)]
    },
    fallbacks=[],
    name="filter_conv",
    persistent=False
)

notifications_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("settings_notifications", settings_notifications)],
    states={
        NOTIF_1H: [CallbackQueryHandler(notif_1h_callback)],
        NOTIF_15M: [CallbackQueryHandler(notif_15m_callback)],
        NOTIF_5M: [CallbackQueryHandler(notif_5m_callback)],
        NOTIF_NEW: [CallbackQueryHandler(notif_new_callback)],
    },
    fallbacks=[],
    name="notifications_conv",
    persistent=False
)

start_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        FILTER_CHOICE: [CallbackQueryHandler(filter_callback)],
        NOTIF_1H: [CallbackQueryHandler(notif_1h_callback)],
        NOTIF_15M: [CallbackQueryHandler(notif_15m_callback)],
        NOTIF_5M: [CallbackQueryHandler(notif_5m_callback)],
        NOTIF_NEW: [CallbackQueryHandler(notif_new_callback)],
    },
    fallbacks=[],
    name="start_conv",
    persistent=False
)
