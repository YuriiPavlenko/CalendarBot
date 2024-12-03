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

    conn = get_db_connection()
    with conn:
        conn.execute('''
            INSERT INTO user_languages (user_id, language)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET language=excluded.language
        ''', (user_id, language))
    conn.close()

    logging.info(f"User {user_id} set language to {language}")
    query.edit_message_text(text=f"Мова встановлена на {language}.")

def get_user_language(user_id):
    conn = get_db_connection()
    language = 'uk'  # Default to Ukrainian
    with conn:
        row = conn.execute('SELECT language FROM user_languages WHERE user_id = ?', (user_id,)).fetchone()
        if row:
            language = row['language']
    conn.close()
    return language