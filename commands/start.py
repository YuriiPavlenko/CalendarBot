from telegram import Update
from telegram.ext import CallbackContext
from commands.settings import settings
from commands.settings import get_user_language
from localization import get_texts

def start(update: Update, context: CallbackContext):
    """Sends a greeting message and asks for language preference."""
    language = get_user_language(update.effective_user.id)
    texts = get_texts(language)
    update.message.reply_text(texts['choose_language'])
    settings(update, context) 