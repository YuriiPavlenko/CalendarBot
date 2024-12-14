import logging
import logging.config

logging.config.fileConfig("src/logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

from telegram import BotCommand
from telegram.ext import Application
from .config import TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_URL, WEBHOOK_PORT
from .start import start_handler
from .gets import (get_today_handler, get_tomorrow_handler, get_rest_week_handler, get_next_week_handler)
from .notifications import refresh_meetings, notification_job
from .localization import STRINGS

async def error_handler(update, context):
    logger.error(f"Exception while handling an update: {update}", exc_info=context.error)

async def startup(application):
    await refresh_meetings()
    application.job_queue.run_repeating(refresh_meetings, interval=300)
    application.job_queue.run_repeating(notification_job, interval=60)
    logger.info("Startup tasks completed.")

if __name__ == "__main__":
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Basic handlers
    application.add_error_handler(error_handler)
    application.add_handler(start_handler)
    application.add_handler(get_today_handler)
    application.add_handler(get_tomorrow_handler)
    application.add_handler(get_rest_week_handler)
    application.add_handler(get_next_week_handler)

    async def post_init(app):
        await app.bot.set_my_commands([
            BotCommand("start", STRINGS["menu_start"]),
            BotCommand("get_today", STRINGS["menu_get_today"]),
            BotCommand("get_tomorrow", STRINGS["menu_get_tomorrow"]),
            BotCommand("get_rest_week", STRINGS["menu_get_rest_week"]),
            BotCommand("get_next_week", STRINGS["menu_get_next_week"]),
        ])
        await startup(app)

    application.post_init = post_init
    application.run_webhook(
        listen="0.0.0.0",
        port=int(WEBHOOK_PORT),
        url_path="",
        webhook_url=TELEGRAM_WEBHOOK_URL
    )
