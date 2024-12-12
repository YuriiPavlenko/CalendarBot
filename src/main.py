import logging
import logging.config

logging.config.fileConfig("src/logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

from telegram import BotCommand
from telegram.ext import Application
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_URL, WEBHOOK_PORT
from .handlers.start import start_handler
from .handlers.gets import (get_today_handler, get_tomorrow_handler, get_rest_week_handler, get_next_week_handler)
from .notifications import initialize_notifications_variables, refresh_meetings, notification_job
from .localization import STRINGS

async def error_handler(update, context):
    logger.error("Unhandled exception occurred", exc_info=True)

async def startup(application):
    # Initialize meetings without using the cache
    await refresh_meetings(initial_run=True)
    # Schedule recurring jobs
    application.job_queue.run_repeating(refresh_meetings, interval=300, first=300)
    application.job_queue.run_repeating(notification_job, interval=60, first=60)

if __name__ == "__main__":
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_error_handler(error_handler)
    application.add_handler(start_handler)
    application.add_handler(get_today_handler)
    application.add_handler(get_tomorrow_handler)
    application.add_handler(get_rest_week_handler)
    application.add_handler(get_next_week_handler)

    # Initialize notification logic
    initialize_notifications_variables(application)

    # run_webhook is async but we can use the post_init hook to run startup tasks
    async def post_init(app):
        await startup(app)

     # Async function to set commands
    async def set_commands():
        await application.bot.set_my_commands([
            BotCommand("start", STRINGS["menu_start"]),
            BotCommand("get_today", STRINGS["menu_get_today"]),
            BotCommand("get_tomorrow", STRINGS["menu_get_tomorrow"]),
            BotCommand("get_rest_week", STRINGS["menu_get_rest_week"]),
            BotCommand("get_next_week", STRINGS["menu_get_next_week"]),
        ])

    # Post-initialization tasks
    async def post_init(app):
        logger.debug("Setting commands...")
        await set_commands()  # Await the set_commands coroutine
        logger.debug("Commands set successfully.")
        await startup(app)  # Include your startup tasks here if needed

    # Attach the post_init hook
    application.post_init = post_init

    application.run_webhook(
        listen="0.0.0.0",
        port=int(WEBHOOK_PORT),
        url_path="",
        webhook_url=TELEGRAM_WEBHOOK_URL
    )
