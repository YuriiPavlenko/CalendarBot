import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, CommandHandler
from ..database import SessionLocal, set_filter, set_notifications
from localization import STRINGS
from .notifications import ask_notification_1h, NOTIF_1H, NOTIF_15M, NOTIF_5M, NOTIF_NEW

logger = logging.getLogger(__name__)

FILTER_CHOICE = 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info("User %s started bot", user_id)
    await update.message.reply_text(STRINGS["greeting"])

    keyboard = [
        [InlineKeyboardButton(STRINGS["settings_filter_all"], callback_data="all"),
         InlineKeyboardButton(STRINGS["settings_filter_mine"], callback_data="mine")]
    ]
    await update.message.reply_text(STRINGS["settings_filter_intro"],
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    context.user_data["from_start"] = True
    return FILTER_CHOICE

async def filter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    choice = query.data  # "all" or "mine"
    session = SessionLocal()
    set_filter(session, user_id, choice)
    session.close()
    await query.edit_message_text(text=STRINGS["settings_filter_saved"])

    # Proceed to notifications since we came from start
    context.user_data["from_start"] = True
    # Move to ask_notification_1h
    return await ask_notification_1h(query.message, context)

start_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        FILTER_CHOICE: [CallbackQueryHandler(filter_callback)],
        NOTIF_1H: [CallbackQueryHandler(lambda u,c: c.dispatcher.handlers[NOTIF_1H][0].callback(u,c))],
        NOTIF_15M: [CallbackQueryHandler(lambda u,c: c.dispatcher.handlers[NOTIF_15M][0].callback(u,c))],
        NOTIF_5M: [CallbackQueryHandler(lambda u,c: c.dispatcher.handlers[NOTIF_5M][0].callback(u,c))],
        NOTIF_NEW: [CallbackQueryHandler(lambda u,c: c.dispatcher.handlers[NOTIF_NEW][0].callback(u,c))]
    },
    fallbacks=[],
    name="start_conv",
    persistent=False
)
