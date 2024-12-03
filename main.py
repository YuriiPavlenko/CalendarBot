import os
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from handlers.start import start, language_choice
from handlers.calendar import show_meetings, show_user_meetings
from handlers.notifications import manage_notifications, subscribe_notifications, unsubscribe_notifications
from handlers.meetings import create_meeting
from utils.database import initialize_db

logging.basicConfig(level=logging.INFO)

async def main():
    initialize_db()  # Initialize the database

    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL')  # Ensure this is set in your environment

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(language_choice, pattern='^lang_'))
    application.add_handler(CommandHandler('show_meetings', show_meetings))
    application.add_handler(CommandHandler('show_user_meetings', show_user_meetings))
    application.add_handler(CommandHandler('manage_notifications', manage_notifications))
    application.add_handler(CommandHandler('subscribe_notifications', subscribe_notifications))
    application.add_handler(CommandHandler('unsubscribe_notifications', unsubscribe_notifications))
    application.add_handler(CommandHandler('create_meeting', create_meeting))

    # Set webhook
    await application.bot.set_webhook(url=TELEGRAM_WEBHOOK_URL)

    # Start the application
    await application.start()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())