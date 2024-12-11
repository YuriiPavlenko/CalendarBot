import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler
)
from ..database import SessionLocal, set_filter, set_notifications
from ..localization import STRINGS

logger = logging.getLogger(__name__)

# States
FILTER_CHOICE = 1
NOTIF_1H = 2
NOTIF_15M = 3
NOTIF_5M = 4
NOTIF_NEW = 5

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User %s started the bot", update.effective_user.id)
    await update.message.reply_text(STRINGS["greeting"])
    # Immediately ask for filter choice
    keyboard = [
        [InlineKeyboardButton(STRINGS["settings_filter_all"], callback_data="all"),
         InlineKeyboardButton(STRINGS["settings_filter_mine"], callback_data="mine")]
    ]
    await update.message.reply_text(STRINGS["settings_filter_intro"],
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    context.user_data["from_start"] = True
    return FILTER_CHOICE

async def filter_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    choice = query.data  # "all" or "mine"

    # Save filter choice
    session = SessionLocal()
    set_filter(session, user_id, choice)
    session.close()

    await query.edit_message_text(text=STRINGS["settings_filter_saved"])
    # Now ask about notifications
    keyboard = [
        [InlineKeyboardButton(STRINGS["yes_button"], callback_data="yes"),
         InlineKeyboardButton(STRINGS["no_button"], callback_data="no")]
    ]
    await query.message.reply_text(STRINGS["settings_notifications_intro"] + "\n" + STRINGS["settings_notifications_1h"],
                                   reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_1H

async def notif_1h_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["notify_1h"] = (query.data == "yes")

    keyboard = [
        [InlineKeyboardButton(STRINGS["yes_button"], callback_data="yes"),
         InlineKeyboardButton(STRINGS["no_button"], callback_data="no")]
    ]
    await query.edit_message_text(text=STRINGS["settings_notifications_15m"], reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_15M

async def notif_15m_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["notify_15m"] = (query.data == "yes")

    keyboard = [
        [InlineKeyboardButton(STRINGS["yes_button"], callback_data="yes"),
         InlineKeyboardButton(STRINGS["no_button"], callback_data="no")]
    ]
    await query.edit_message_text(text=STRINGS["settings_notifications_5m"], reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_5M

async def notif_5m_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["notify_5m"] = (query.data == "yes")

    keyboard = [
        [InlineKeyboardButton(STRINGS["yes_button"], callback_data="yes"),
         InlineKeyboardButton(STRINGS["no_button"], callback_data="no")]
    ]
    await query.edit_message_text(text=STRINGS["settings_notifications_new"], reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_NEW

async def notif_new_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["notify_new"] = (query.data == "yes")

    user_id = query.from_user.id
    session = SessionLocal()
    set_notifications(session, user_id,
                      context.user_data.get("notify_1h", False),
                      context.user_data.get("notify_15m", False),
                      context.user_data.get("notify_5m", False),
                      context.user_data.get("notify_new", False))
    session.close()

    await query.edit_message_text(text=STRINGS["settings_notifications_saved"])

    # Show all commands now
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

start_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        FILTER_CHOICE: [CallbackQueryHandler(filter_chosen)],
        NOTIF_1H: [CallbackQueryHandler(notif_1h_callback)],
        NOTIF_15M: [CallbackQueryHandler(notif_15m_callback)],
        NOTIF_5M: [CallbackQueryHandler(notif_5m_callback)],
        NOTIF_NEW: [CallbackQueryHandler(notif_new_callback)]
    },
    fallbacks=[],
    name="start_conv",
    persistent=False
)
