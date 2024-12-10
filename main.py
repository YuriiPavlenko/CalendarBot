import logging
import logging.config
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.ext import ContextTypes
from src.handlers import start, settings_filter, filter_chosen, settings_notifications, notifications_chosen, get_today, get_tomorrow, get_rest_week, get_next_week
from src.config import TELEGRAM_BOT_TOKEN, WEBHOOK_HOST, WEBHOOK_PORT
from src.localization import STRINGS

logging.config.fileConfig("src/logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

# Use Flask to receive webhooks
app = Flask(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

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

# Telegram webhook endpoint
@app.route("/", methods=["POST", "GET"])
def webhook():
    if request.method == "POST":
        try:
            update = Update.de_json(request.get_json(force=True), bot)
            application.update_queue.put(update)
        except Exception as e:
            logger.error("Error processing update: %s", e)
        return "OK"
    return "Hello, I am a bot!"

if __name__ == "__main__":
    # Set webhook
    bot.set_webhook(url=WEBHOOK_HOST)
    # Start Flask
    app.run(host="0.0.0.0", port=WEBHOOK_PORT, ssl_context='adhoc')
