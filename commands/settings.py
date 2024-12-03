from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_db_connection
import logging
from localization import get_texts

logging.basicConfig(level=logging.INFO)

def settings(update, context):
    """Allows the user to choose a language."""
    language = get_user_language(update.effective_user.id)
    texts = get_texts(language)

    keyboard = [
        [InlineKeyboardButton("Українська", callback_data='lang_uk')],
        [InlineKeyboardButton("Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("English", callback_data='lang_en')],
        [InlineKeyboardButton("ไทย", callback_data='lang_th')],
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

def get_user_language(user_id):
    logging.info(f"Retrieving language for user {user_id}")
    language = 'uk'  # Default to Ukrainian
    try:
        conn = get_db_connection()
        logging.info("Database connection established for retrieval")
        with conn:
            row = conn.execute('SELECT language FROM user_languages WHERE user_id = ?', (user_id,)).fetchone()
            if row:
                language = row['language']
                logging.info(f"Retrieved language for user {user_id}: {language}")
            else:
                logging.info(f"No language set for user {user_id}, defaulting to Ukrainian")
    except Exception as e:
        logging.error(f"Error retrieving language for user {user_id}: {e}")
    finally:
        conn.close()
        logging.info("Database connection closed after retrieval")
    return language