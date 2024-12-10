import os
import logging
import logging.config
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from src.handlers import start, settings_filter, filter_chosen, settings_notifications, notifications_chosen, get_today, get_tomorrow, get_rest_week, get_next_week
from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_URL  # Make sure this URL is set and valid.
from src.localization import STRINGS

logging.config.fileConfig("src/logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# Use the PORT provided by Railway, or default to 3000 if not set
PORT = int(os.environ.get("PORT", "443"))

application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

filter_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("settings_filter", settings_filter)],
    states={
        0: [MessageHandler(filters.TEXT, filter_chosen)]
    },
    fallbacks=[]
)

notif_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("settings_notifications", settings_notifications)],
    states={
        0: [MessageHandler(filters.TEXT & ~filters.COMMAND, notifications_chosen)]
    },
    fallbacks=[]
)

application.add_handler(CommandHandler("start", start))
application.add_handler(filter_conv_handler)
application.add_handler(notif_conv_handler)
application.add_handler(CommandHandler("get_today", get_today))
application.add_handler(CommandHandler("get_tomorrow", get_tomorrow))
application.add_handler(CommandHandler("get_rest_week", get_rest_week))
application.add_handler(CommandHandler("get_next_week", get_next_week))

if __name__ == "__main__":
    # Run the application using its built-in webhook server.
    # Make sure TELEGRAM_WEBHOOK_URL is something like "https://<your-app>.up.railway.app"
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="",  # If you like, you can specify a path, e.g. "/webhook"
        webhook_url=TELEGRAM_WEBHOOK_URL
    )
