from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from ..database import SessionLocal, set_notifications
from ..localization import STRINGS

NOTIF_1H = 2
NOTIF_15M = 3
NOTIF_5M = 4
NOTIF_NEW = 5

async def ask_notification_1h(message, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(STRINGS["yes_button"], callback_data="yes"), InlineKeyboardButton(STRINGS["no_button"], callback_data="no")]
    ]
    await message.reply_text(STRINGS["settings_notifications_intro"] + "\n" + STRINGS["settings_notifications_1h"],
                             reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_1H

async def notif_1h_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data["notify_1h"] = (choice == "yes")
    # Ask about 15m
    keyboard = [
        [InlineKeyboardButton(STRINGS["yes_button"], callback_data="yes"), InlineKeyboardButton(STRINGS["no_button"], callback_data="no")]
    ]
    await query.edit_message_text(text=STRINGS["settings_notifications_15m"], reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_15M

async def notif_15m_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data["notify_15m"] = (choice == "yes")
    # Ask about 5m
    keyboard = [
        [InlineKeyboardButton(STRINGS["yes_button"], callback_data="yes"), InlineKeyboardButton(STRINGS["no_button"], callback_data="no")]
    ]
    await query.edit_message_text(text=STRINGS["settings_notifications_5m"], reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_5M

async def notif_5m_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data["notify_5m"] = (choice == "yes")
    # Ask about new meeting
    keyboard = [
        [InlineKeyboardButton(STRINGS["yes_button"], callback_data="yes"), InlineKeyboardButton(STRINGS["no_button"], callback_data="no")]
    ]
    await query.edit_message_text(text=STRINGS["settings_notifications_new"], reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_NEW

async def notif_new_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    context.user_data["notify_new"] = (choice == "yes")

    user_id = query.from_user.id
    session = SessionLocal()
    set_notifications(session, user_id,
                      context.user_data.get("notify_1h", False),
                      context.user_data.get("notify_15m", False),
                      context.user_data.get("notify_5m", False),
                      context.user_data.get("notify_new", False))
    session.close()

    await query.edit_message_text(text=STRINGS["settings_notifications_saved"])

    # If we came from start, show menu and done message
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

notifications_conv_handler = ConversationHandler(
    entry_points=[],
    states={
        NOTIF_1H: [InlineKeyboardButton],
        NOTIF_15M: [InlineKeyboardButton],
        NOTIF_5M: [InlineKeyboardButton],
        NOTIF_NEW: [InlineKeyboardButton],
    },
    fallbacks=[],
    name="notifications_conv",
    persistent=False
)
