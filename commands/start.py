from telegram import Update
from telegram.ext import CallbackContext
from commands.settings import settings

def start(update: Update, context: CallbackContext):
    """Sends a greeting message and asks for language preference."""
    update.message.reply_text("Ласкаво просимо! Будь ласка, оберіть свою мову:")
    settings(update, context) 