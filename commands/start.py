from telegram import Update
from telegram.ext import CallbackContext
from commands.settings import settings

def start(update: Update, context: CallbackContext):
    """Sends a greeting message and asks for language preference."""
    update.message.reply_text("Welcome! Please choose your language:")
    settings(update, context) 