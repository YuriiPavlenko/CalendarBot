import logging
import logging.config
import sys

logging.config.fileConfig("src/logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

import os
from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_URL, WEBHOOK_PORT
from handlers.start import start_handler
from handlers.gets import (get_today_handler, get_tomorrow_handler, get_rest_week_handler, get_next_week_handler)
from scheduler import scheduler  # We'll explicitly start it below

async def error_handler(update, context):
    logger.exception("Unhandled exception", extra={"update": str(update), "error": str(context.error)})

def main():
    # Initialize Telegram application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_error_handler(error_handler)

    # Add handlers
    application.add_handler(start_handler)
    application.add_handler(get_today_handler)
    application.add_handler(get_tomorrow_handler)
    application.add_handler(get_rest_week_handler)
    application.add_handler(get_next_week_handler)

    # Explicitly start the scheduler so that it's clear
    # that the periodic jobs run from here.
    logger.info("Starting scheduler...")
    scheduler.start()

    logger.debug("Running webhook...", extra={"context": "webhook_setup"})
    application.run_webhook(
        listen="0.0.0.0",
        port=int(WEBHOOK_PORT),
        url_path="",
        webhook_url=TELEGRAM_WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
