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
from localization import get_texts

logging.basicConfig(level=logging.INFO)

def handle_message(update, context):
    text = update.message.text
    user_id = update.effective_user.id
    language = get_user_language(user_id)  # Retrieve language from the database
    texts = get_texts(language)

    logging.info(f"User {user_id} sent message: {text} in language: {language}")

    if text == texts['meetings_today']:
        send_today_meetings(update, context)
    elif text == texts['meetings_tomorrow']:
        send_tomorrow_meetings(update, context)
    elif text == texts['meetings_today'] + " та " + texts['meetings_tomorrow']:
        send_today_tomorrow_meetings(update, context)
    elif text == texts['meetings_this_week']:
        send_week_meetings(update, context)
    elif text == texts['meetings_next_week']:
        send_next_week_meetings(update, context)

def set_language(update, context):
    query = update.callback_query
    user_id = update.effective_user.id
    language = query.data

    # Update the user's language in the database
    update_user_language(user_id, language)

    # Refresh the command descriptions based on the new language
    texts = get_texts(language)
    command_descriptions = texts['command_descriptions']
    context.bot.set_my_commands([BotCommand(cmd, desc) for cmd, desc in command_descriptions])

    query.edit_message_text(text=texts['language_set'])

def main():
    initialize_db()  # Initialize the database
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    TELEGRAM_WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL')

    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Set bot commands for the menu based on the default language
    default_language = 'uk'  # Set your default language here
    command_descriptions = get_texts(default_language)['command_descriptions']
    updater.bot.set_my_commands([BotCommand(cmd, desc) for cmd, desc in command_descriptions])

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
