import os
import logging
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram import BotCommand
from commands.today import send_today_meetings
from commands.tomorrow import send_tomorrow_meetings
from commands.today_tomorrow import send_today_tomorrow_meetings
from commands.week import send_week_meetings
from commands.next_week import send_next_week_meetings
from commands.start import start
from commands.settings import get_user_language, settings, set_language
from database import initialize_db

logging.basicConfig(level=logging.INFO)

def handle_message(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    language = get_user_language(user_id)  # Retrieve language from the database

    logging.info(f"User {user_id} sent message: {text} in language: {language}")

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
    initialize_db()  # Initialize the database
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL')

    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Language-specific command descriptions
    command_descriptions = {
        'uk': [
            BotCommand("start", "Почати взаємодію з ботом"),
            BotCommand("today", "Отримати зустрічі на сьогодні"),
            BotCommand("tomorrow", "Отримати зустрічі на завтра"),
            BotCommand("today_tomorrow", "Отримати зустрічі на сьогодні та завтра"),
            BotCommand("week", "Отримати зустрічі на цей тиждень"),
            BotCommand("next_week", "Отримати зустрічі на наступний тиждень")
        ],
        'ru': [
            BotCommand("start", "Начать взаимодействие с ботом"),
            BotCommand("today", "Получить встречи на сегодня"),
            BotCommand("tomorrow", "Получить встречи на завтра"),
            BotCommand("today_tomorrow", "Получить встречи на сегодня и завтра"),
            BotCommand("week", "Получить встречи на эту неделю"),
            BotCommand("next_week", "Получить встречи на следующую неделю")
        ],
        'en': [
            BotCommand("start", "Start interacting with the bot"),
            BotCommand("today", "Get today's meetings"),
            BotCommand("tomorrow", "Get tomorrow's meetings"),
            BotCommand("today_tomorrow", "Get today's and tomorrow's meetings"),
            BotCommand("week", "Get this week's meetings"),
            BotCommand("next_week", "Get next week's meetings")
        ],
        'th': [
            BotCommand("start", "เริ่มโต้ตอบกับบอท"),
            BotCommand("today", "รับการประชุมวันนี้"),
            BotCommand("tomorrow", "รับการประชุมพรุ่งนี้"),
            BotCommand("today_tomorrow", "รับการประชุมวันนี้และพรุ่งนี้"),
            BotCommand("week", "รับการประชุมสัปดาห์นี้"),
            BotCommand("next_week", "รับการประชุมสัปดาห์หน้า")
        ]
    }

    # Set bot commands for the menu based on the default language
    updater.bot.set_my_commands(command_descriptions['uk'])

    # Command to start the bot and show buttons
    dispatcher.add_handler(CommandHandler('start', start))

    # Command handlers for functional commands
    dispatcher.add_handler(CommandHandler('today', send_today_meetings))
    dispatcher.add_handler(CommandHandler('tomorrow', send_tomorrow_meetings))
    dispatcher.add_handler(CommandHandler('today_tomorrow', send_today_tomorrow_meetings))
    dispatcher.add_handler(CommandHandler('week', send_week_meetings))
    dispatcher.add_handler(CommandHandler('next_week', send_next_week_meetings))

    # Command handler for settings
    dispatcher.add_handler(CommandHandler('settings', settings))

    # Callback query handler for language selection
    dispatcher.add_handler(CallbackQueryHandler(set_language))

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
