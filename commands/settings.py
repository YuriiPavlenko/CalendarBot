from telegram import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from database import get_db_connection
import logging
from localization import get_texts

logging.basicConfig(level=logging.INFO)

def get_user_language(user_id):
    """Retrieve the user's language from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'en'  # Default to English if not set

def update_user_language(user_id, language):
    """Update the user's language in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, language) VALUES (?, ?)", (user_id, language))
    conn.commit()
    conn.close()

def settings(update, context):
    """Allows the user to choose a language."""
    language = get_user_language(update.effective_user.id)
    texts = get_texts(language)

    keyboard = [
        [InlineKeyboardButton("Українська", callback_data='uk')],
        [InlineKeyboardButton("Русский", callback_data='ru')],
        [InlineKeyboardButton("English", callback_data='en')],
        [InlineKeyboardButton("ภาษาไทย", callback_data='th')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(texts['choose_language'], reply_markup=reply_markup)

def set_language(update, context):
    query = update.callback_query
    user_id = update.effective_user.id
    language = query.data

    # Update the user's language in the database
    update_user_language(user_id, language)

    # Refresh the command descriptions based on the new language
    texts = get_texts(language)
    command_descriptions = texts['command_descriptions']
    
    try:
        context.bot.set_my_commands([BotCommand(cmd, desc) for cmd, desc in command_descriptions])
        logging.info(f"Commands updated for user {user_id} with language {language}")
    except Exception as e:
        logging.error(f"Error updating commands for user {user_id}: {e}")

    query.edit_message_text(text=texts['language_set'])