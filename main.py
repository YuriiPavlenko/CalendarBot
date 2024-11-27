import os
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters
from telegram import BotCommand
from commands.today import send_today_meetings
from commands.tomorrow import send_tomorrow_meetings
from commands.today_tomorrow import send_today_tomorrow_meetings
from commands.week import send_week_meetings
from commands.next_week import send_next_week_meetings
from commands.start import start

def handle_message(update, context):
    text = update.message.text
    if text == 'Зустрічі на сьогодні':
        send_today_meetings(update, context)
    elif text == 'Зустрічі на завтра':
        send_tomorrow_meetings(update, context)
    elif text == 'Зустрічі на сьогодні та завтра':
        send_today_tomorrow_meetings(update, context)
    elif text == 'Зустрічі на цей тиждень':
        send_week_meetings(update, context)
    elif text == 'Зустрічі на наступний тиждень':
        send_next_week_meetings(update, context)

def main():
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL')

    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Set bot commands for the menu
    updater.bot.set_my_commands([
        BotCommand("start", "Почати взаємодію з ботом"),
        BotCommand("today", "Отримати зустрічі на сьогодні"),
        BotCommand("tomorrow", "Отримати зустрічі на завтра"),
        BotCommand("today_tomorrow", "Отримати зустрічі на сьогодні та завтра"),
        BotCommand("week", "Отримати зустрічі на цей тиждень"),
        BotCommand("next_week", "Отримати зустрічі на наступний тиждень")
    ])

    # Command to start the bot and show buttons
    dispatcher.add_handler(CommandHandler('start', start))

    # Command handlers for functional commands
    dispatcher.add_handler(CommandHandler('today', send_today_meetings))
    dispatcher.add_handler(CommandHandler('tomorrow', send_tomorrow_meetings))
    dispatcher.add_handler(CommandHandler('today_tomorrow', send_today_tomorrow_meetings))
    dispatcher.add_handler(CommandHandler('week', send_week_meetings))
    dispatcher.add_handler(CommandHandler('next_week', send_next_week_meetings))

    # Handle custom keyboard inputs
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the webhook
    updater.start_webhook(
        listen="0.0.0.0",
        port=443,  # Use port 443 for HTTPS
        url_path=TELEGRAM_BOT_TOKEN,
        webhook_url=f"{TELEGRAM_WEBHOOK_URL}/{TELEGRAM_BOT_TOKEN}"
    )

    updater.idle()

if __name__ == '__main__':
    main()
