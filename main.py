import os
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters
from telegram import BotCommand
from commands.today_tomorrow import send_today_tomorrow_events
from commands.week import send_week_events
from commands.start import start

def handle_message(update, context):
    text = update.message.text
    if text == 'Події на сьогодні та завтра':
        send_today_tomorrow_events(update, context)
    elif text == 'Події на цей тиждень':
        send_week_events(update, context)

def main():
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL')  # Set this to your app's URL

    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Set bot commands for the menu
    updater.bot.set_my_commands([
        BotCommand("start", "Почати взаємодію з ботом"),
        BotCommand("getevents", "Отримати події на сьогодні та завтра"),
        BotCommand("getweekevents", "Отримати події на цей тиждень")
    ])

    # Command to start the bot and show buttons
    dispatcher.add_handler(CommandHandler('start', start))

    # Handle custom keyboard inputs
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the webhook
    updater.start_webhook(
        listen="0.0.0.0",
        port=443,  # Use a port that your server can listen to
        url_path=TELEGRAM_BOT_TOKEN,
        webhook_url=f"{TELEGRAM_WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    )

    updater.idle()

if __name__ == '__main__':
    main()
