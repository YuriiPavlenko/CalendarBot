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

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
