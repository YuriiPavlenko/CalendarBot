from telegram import Update
from telegram.ext import CallbackContext

def start(update: Update, context: CallbackContext):
    """Sends a greeting message to the user."""
    # Greeting message
    greeting_message = (
        "Привіт! Я ваш бот для календаря. "
        "Використовуйте меню команд, щоб взаємодіяти зі мною."
    )

    # Send the greeting message
    update.message.reply_text(greeting_message) 