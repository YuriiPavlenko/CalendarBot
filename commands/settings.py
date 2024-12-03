from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from database import get_db_connection
import logging

logging.basicConfig(level=logging.INFO)

def settings(update, context):
    """Allows the user to choose a language."""
    keyboard = [
        [InlineKeyboardButton("Українська", callback_data='lang_uk')],
        [InlineKeyboardButton("Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("English", callback_data='lang_en')],
        [InlineKeyboardButton("ไทย", callback_data='lang_th')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Будь ласка, оберіть свою мову:', reply_markup=reply_markup)

def set_language(update, context):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    language = query.data.split('_')[1]

    logging.info(f"Attempting to set language for user {user_id} to {language}")

    try:
        conn = get_db_connection()
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

    query.edit_message_text(text=f"Мова встановлена на {language}.")

def get_user_language(user_id):
    logging.info(f"Retrieving language for user {user_id}")
    language = 'uk'  # Default to Ukrainian
    try:
        conn = get_db_connection()
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
    return language