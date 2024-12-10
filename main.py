import logging
import logging.config
import sys

# Load logging configuration
logging.config.fileConfig("src/logging.conf", disable_existing_loggers=False)

from telegram.ext import Application, CommandHandler
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_URL, WEBHOOK_PORT
from src.localization import STRINGS

from src.handlers.start import start_conv_handler
from src.handlers.filter import filter_conv_handler
from src.handlers.notifications import (ask_notification_1h, notif_1h_callback, notif_15m_callback, notif_5m_callback, notif_new_callback, NOTIF_1H, NOTIF_15M, NOTIF_5M, NOTIF_NEW)
from src.handlers.gets import get_today, get_tomorrow, get_rest_week, get_next_week

from telegram.ext import ConversationHandler, CallbackQueryHandler

logger = logging.getLogger(__name__)
logger.info("Bot starting up", extra={"context": "initialization"})

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

NOTIF_COMMAND = ConversationHandler(
    entry_points=[CommandHandler("settings_notifications", lambda u,c: ask_notification_1h(u.message, c))],
    states={
        NOTIF_1H: [CallbackQueryHandler(notif_1h_callback)],
        NOTIF_15M: [CallbackQueryHandler(notif_15m_callback)],
        NOTIF_5M: [CallbackQueryHandler(notif_5m_callback)],
        NOTIF_NEW: [CallbackQueryHandler(notif_new_callback)]
    },
    fallbacks=[],
    name="notif_command",
    persistent=False,
    per_message=True
)

application.add_handler(start_conv_handler)
application.add_handler(filter_conv_handler)
application.add_handler(NOTIF_COMMAND)
application.add_handler(CommandHandler("get_today", get_today))
application.add_handler(CommandHandler("get_tomorrow", get_tomorrow))
application.add_handler(CommandHandler("get_rest_week", get_rest_week))
application.add_handler(CommandHandler("get_next_week", get_next_week))

if __name__ == "__main__":
    logger.debug("Running webhook...", extra={"context": "webhook_setup"})
    application.run_webhook(
        listen="0.0.0.0",
        port=int(WEBHOOK_PORT),
        url_path="",
        webhook_url=TELEGRAM_WEBHOOK_URL
    )