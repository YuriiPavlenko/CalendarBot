from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.database import Session, User
from utils.localization import get_texts

def start(update: Update, context: CallbackContext):
    """Sends a greeting message and asks for language preference."""
    session = Session()
    user_id = update.effective_user.id
    user = session.query(User).filter_by(telegram_id=user_id).first()

    if not user:
        user = User(telegram_id=user_id)
        session.add(user)
        session.commit()

    texts = get_texts(user.language)

    # Greet the user
    update.message.reply_text(texts['greeting'])

    # Prompt the user to choose a language
    keyboard = [
        [InlineKeyboardButton("Українська", callback_data='lang_uk')],
        [InlineKeyboardButton("Русский", callback_data='lang_ru')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(texts['choose_language'], reply_markup=reply_markup)

def language_choice(update: Update, context: CallbackContext):
    """Handles the language choice and sends confirmation in the chosen language."""
    query = update.callback_query
    user_id = update.effective_user.id
    language = query.data.split('_')[1]

    session = Session()
    user = session.query(User).filter_by(telegram_id=user_id).first()
    user.language = language
    session.commit()

    # Get texts in the chosen language
    texts = get_texts(language)

    # Confirm the language setting
    query.edit_message_text(texts['language_set'])

    # Display available commands and their descriptions
    commands_list = "\n".join([f"/{cmd} - {desc}" for cmd, desc in texts['command_descriptions']])
    context.bot.send_message(chat_id=query.message.chat_id, text=f"{texts['available_commands']}\n{commands_list}\n\n{texts['menu_notice']}")
