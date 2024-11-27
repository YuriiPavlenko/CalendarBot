import os
from telegram.ext import CommandHandler, Updater
from commands.today_tomorrow import send_today_tomorrow_events
from commands.week import send_week_events

def main():
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL')

    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Command to fetch today's and tomorrow's events
    dispatcher.add_handler(CommandHandler('getevents', send_today_tomorrow_events))

    # Command to fetch all events for the week
    dispatcher.add_handler(CommandHandler('getweekevents', send_week_events))

    # Start the webhook
    updater.start_webhook(listen="0.0.0.0",
                          port=443,
                          url_path=TELEGRAM_BOT_TOKEN,
                          webhook_url=f"{TELEGRAM_WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}")

    updater.idle()

if __name__ == '__main__':
    main()
