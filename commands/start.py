from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

def start(update: Update, context: CallbackContext):
    """Sends a message with buttons to interact with the bot."""
    keyboard = [
        [InlineKeyboardButton("Події на сьогодні та завтра", callback_data='getevents')],
        [InlineKeyboardButton("Події на цей тиждень", callback_data='getweekevents')]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Виберіть команду:', reply_markup=reply_markup) 