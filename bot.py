import os
import logging
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from handlers.start import start, language_choice
from handlers.calendar import show_meetings
from handlers.notifications import manage_notifications
from handlers.meetings import create_meeting
from utils.database import initialize_db

logging.basicConfig(level=logging.INFO)

def main():
    initialize_db()  # Initialize the database

    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(language_choice, pattern='^lang_'))
    dispatcher.add_handler(CommandHandler('show_meetings', show_meetings))
    dispatcher.add_handler(CommandHandler('manage_notifications', manage_notifications))
    dispatcher.add_handler(CommandHandler('create_meeting', create_meeting))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()