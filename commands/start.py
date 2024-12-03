from telegram import Update
from telegram.ext import CallbackContext
from commands.settings import settings, update_user_language
from commands.settings import get_user_language
from localization import get_texts

def start(update: Update, context: CallbackContext):
    """Sends a greeting message, asks for language preference, and displays available commands."""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    texts = get_texts(language)

    # Greet the user
    update.message.reply_text(texts['greeting'])

    # Prompt the user to choose a language
    settings(update, context)

    # Confirm the language setting
    language = get_user_language(user_id)
    texts = get_texts(language)
    update.message.reply_text(texts['language_set'])

    # Notify the user to restart the app for menu update
    update.message.reply_text(texts['restart_notice'])

    # Display available commands and their descriptions
    commands_list = "\n".join([f"/{cmd} - {desc}" for cmd, desc in texts['command_descriptions']])
    update.message.reply_text(f"{texts['available_commands']}\n{commands_list}\n\n{texts['menu_notice']}") 