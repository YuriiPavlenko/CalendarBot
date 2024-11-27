import os
from telegram.ext import CommandHandler, Updater, CallbackQueryHandler
from commands.today_tomorrow import send_today_tomorrow_events
from commands.week import send_week_events
from commands.start import start

def main():
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command to start the bot and show buttons
    dispatcher.add_handler(CommandHandler('start', start))

    # Command to fetch today's and tomorrow's events
    dispatcher.add_handler(CallbackQueryHandler(send_today_tomorrow_events, pattern='getevents'))

    # Command to fetch all events for the week
    dispatcher.add_handler(CallbackQueryHandler(send_week_events, pattern='getweekevents'))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
