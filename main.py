import logging
import logging.config
import sys
from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_URL, WEBHOOK_PORT
from src.localization import STRINGS

from src.handlers.start import start, start_conv_handler
from src.handlers.filter import filter_conv_handler
from src.handlers.notifications import (
    ask_notification_1h_cmd, notif_1h_cmd_callback, notif_15m_cmd_callback,
    notif_5m_cmd_callback, notif_new_cmd_callback,
    NOTIF_CMD_1H, NOTIF_CMD_15M, NOTIF_CMD_5M, NOTIF_CMD_NEW
)
from src.handlers.gets import get_today, get_tomorrow, get_rest_week, get_next_week

logging.config.fileConfig("src/logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

logger.info("Bot starting up", extra={"context": "initialization"})

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

# Add a global error handler
async def error_handler(update, context):
    logger.exception("Unhandled exception", extra={"update": str(update), "error": str(context.error)})

application.add_error_handler(error_handler)

# Direct handler for /start to ensure it works
application.add_handler(CommandHandler("start", start))

application.add_handler(start_conv_handler)
application.add_handler(filter_conv_handler)

# Separate conversation for /settings_notifications with unique states
NOTIF_COMMAND = ConversationHandler(
    entry_points=[CommandHandler("settings_notifications", lambda u,c: ask_notification_1h_cmd(u.message, c))],
    states={
        NOTIF_CMD_1H: [CallbackQueryHandler(notif_1h_cmd_callback)],
        NOTIF_CMD_15M: [CallbackQueryHandler(notif_15m_cmd_callback)],
        NOTIF_CMD_5M: [CallbackQueryHandler(notif_5m_cmd_callback)],
        NOTIF_CMD_NEW: [CallbackQueryHandler(notif_new_cmd_callback)]
    },
    fallbacks=[],
    name="notif_command",
    persistent=False
)

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
