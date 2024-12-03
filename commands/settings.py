from telegram import InlineKeyboardButton, InlineKeyboardMarkup
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
    query.answer()
    user_id = query.from_user.id
    language = query.data.split('_')[1]

    logging.info(f"User {user_id} clicked to set language to {language}")

    try:
        conn = get_db_connection()
        logging.info("Database connection established")
        with conn:
            conn.execute('''
                INSERT INTO user_languages (user_id, language)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET language=excluded.language
            ''', (user_id, language))
        logging.info(f"Successfully set language for user {user_id} to {language}")
    except Exception as e:
        logging.error(f"Error setting language for user {user_id}: {e}")
    finally:
        conn.close()
        logging.info("Database connection closed")

    try:
        texts = get_texts(language)
        query.edit_message_text(text=texts['language_set'].format(language=language))
        logging.info(f"Confirmation message sent to user {user_id}")
    except Exception as e:
        logging.error(f"Error sending confirmation message to user {user_id}: {e}")