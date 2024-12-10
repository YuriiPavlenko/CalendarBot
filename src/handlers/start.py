import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
from ..database import SessionLocal, set_filter
from ..localization import STRINGS
from .notifications import (ask_notification_1h, notif_1h_callback, notif_15m_callback, notif_5m_callback, notif_new_callback,
                            NOTIF_1H, NOTIF_15M, NOTIF_5M, NOTIF_NEW)

logger = logging.getLogger(__name__)

FILTER_CHOICE = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Entered /start command handler")
    user_id = update.effective_user.id
    logger.info("User %s started bot", user_id)
    await update.message.reply_text(STRINGS["greeting"])
    logger.debug("Sent greeting message")

    keyboard = [
        [InlineKeyboardButton(STRINGS["settings_filter_all"], callback_data="all"),
         InlineKeyboardButton(STRINGS["settings_filter_mine"], callback_data="mine")]
    ]
    await update.message.reply_text(STRINGS["settings_filter_intro"],
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    logger.debug("Sent filter choice inline keyboard")
    context.user_data["from_start"] = True
    return FILTER_CHOICE

async def filter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Entered filter_callback for /start flow")
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    choice = query.data
    logger.debug("User %s chose filter: %s", user_id, choice)
    session = SessionLocal()
    set_filter(session, user_id, choice)
    session.close()
    await query.edit_message_text(text=STRINGS["settings_filter_saved"])
    logger.debug("Filter saved and message edited")

    context.user_data["from_start"] = True
    logger.debug("Proceeding to notifications setup")
    return await ask_notification_1h(query.message, context)

start_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        FILTER_CHOICE: [CallbackQueryHandler(filter_callback)],
        NOTIF_1H: [CallbackQueryHandler(notif_1h_callback)],
        NOTIF_15M: [CallbackQueryHandler(notif_15m_callback)],
        NOTIF_5M: [CallbackQueryHandler(notif_5m_callback)],
        NOTIF_NEW: [CallbackQueryHandler(notif_new_callback)]
    },
    fallbacks=[],
    name="start_conv",
    persistent=False,
    per_message=True
)
