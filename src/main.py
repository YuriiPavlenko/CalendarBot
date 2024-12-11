import logging
import logging.config
import sys
import os

logging.config.fileConfig("src/logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

from telegram.ext import Application
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_URL, WEBHOOK_PORT
from .handlers.start import start_handler
from .handlers.gets import (get_today_handler, get_tomorrow_handler, get_rest_week_handler, get_next_week_handler)
from .scheduler import scheduler, refresh_meetings
import src.notifications  # will set application here

if __name__ == "__main__":
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Provide application to notifications so it can create tasks
    src.notifications.application = application

    # Add handlers
    application.add_handler(start_handler)
    application.add_handler(get_today_handler)
    application.add_handler(get_tomorrow_handler)
    application.add_handler(get_rest_week_handler)
    application.add_handler(get_next_week_handler)

    # Initial fetch to populate cache (no notifications sent on first run)
    refresh_meetings()

    logger.info("Starting scheduler...")
    scheduler.start()

    logger.debug("Running webhook...")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(WEBHOOK_PORT),
        url_path="",
        webhook_url=TELEGRAM_WEBHOOK_URL
    )
