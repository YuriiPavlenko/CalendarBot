import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from ..database import SessionLocal, set_notifications
from ..localization import STRINGS

logger = logging.getLogger(__name__)

# States for the standalone /settings_notifications command
NOTIF_CMD_1H = 201
NOTIF_CMD_15M = 202
NOTIF_CMD_5M = 203
NOTIF_CMD_NEW = 204

async def ask_notification_1h_cmd(message, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Asking user about 1h notifications (cmd)")
    keyboard = [
        [InlineKeyboardButton(STRINGS["yes_button"], callback_data="yes"),
         InlineKeyboardButton(STRINGS["no_button"], callback_data="no")]
    ]
    await message.reply_text(
        STRINGS["settings_notifications_intro"] + "\n" + STRINGS["settings_notifications_1h"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return NOTIF_CMD_1H

async def notif_1h_cmd_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("notif_1h_cmd_callback triggered")
    query = update.callback_query
    await query.answer()
    context.user_data["notify_1h"] = (query.data == "yes")

    keyboard = [
        [InlineKeyboardButton(STRINGS["yes_button"], callback_data="yes"),
         InlineKeyboardButton(STRINGS["no_button"], callback_data="no")]
    ]
    await query.edit_message_text(text=STRINGS["settings_notifications_15m"], reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_CMD_15M

async def notif_15m_cmd_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("notif_15m_cmd_callback triggered")
    query = update.callback_query
    await query.answer()
    context.user_data["notify_15m"] = (query.data == "yes")

    keyboard = [
        [InlineKeyboardButton(STRINGS["yes_button"], callback_data="yes"),
         InlineKeyboardButton(STRINGS["no_button"], callback_data="no")]
    ]
    await query.edit_message_text(text=STRINGS["settings_notifications_5m"], reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_CMD_5M

async def notif_5m_cmd_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("notif_5m_cmd_callback triggered")
    query = update.callback_query
    await query.answer()
    context.user_data["notify_5m"] = (query.data == "yes")

    keyboard = [
        [InlineKeyboardButton(STRINGS["yes_button"], callback_data="yes"),
         InlineKeyboardButton(STRINGS["no_button"], callback_data="no")]
    ]
    await query.edit_message_text(text=STRINGS["settings_notifications_new"], reply_markup=InlineKeyboardMarkup(keyboard))
    return NOTIF_CMD_NEW

async def notif_new_cmd_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("notif_new_cmd_callback triggered")
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
    logger.debug("All notifications saved for /settings_notifications command")

    # After done, we can show a confirmation message (optional)
    await query.message.reply_text(STRINGS["settings_done"])

    return ConversationHandler.END
