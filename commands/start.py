from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler
from commands.settings import update_user_language, get_user_language
from localization import get_texts

def start(update: Update, context: CallbackContext):
    """Sends a greeting message and asks for language preference."""
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    texts = get_texts(language)

    # Greet the user
    update.message.reply_text(texts['greeting'])

    # Prompt the user to choose a language
    keyboard = [
        [InlineKeyboardButton("Українська", callback_data='uk')],
        [InlineKeyboardButton("Русский", callback_data='ru')],
        [InlineKeyboardButton("English", callback_data='en')],
        [InlineKeyboardButton("ภาษาไทย", callback_data='th')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(texts['choose_language'], reply_markup=reply_markup)

def language_choice(update: Update, context: CallbackContext):
    """Handles the language choice and sends confirmation in the chosen language."""
    query = update.callback_query
    user_id = update.effective_user.id
    language = query.data

    # Update the user's language in the database
    update_user_language(user_id, language)

    # Get texts in the chosen language
    texts = get_texts(language)

    # Confirm the language setting
    query.edit_message_text(texts['language_set'])

    # Notify the user to restart the app for menu update
    context.bot.send_message(chat_id=query.message.chat_id, text=texts['restart_notice'])

    # Display available commands and their descriptions
    commands_list = "\n".join([f"/{cmd} - {desc}" for cmd, desc in texts['command_descriptions']])
    context.bot.send_message(chat_id=query.message.chat_id, text=f"{texts['available_commands']}\n{commands_list}\n\n{texts['menu_notice']}")

# Add this handler to your dispatcher in main.py
def add_language_choice_handler(dispatcher):
    dispatcher.add_handler(CallbackQueryHandler(language_choice)) 