import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes, CommandHandler

from ..localization import STRINGS
from ..config import WEB_APP_URL

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("User %s issued /start", update.effective_user.id)
    user_id = update.effective_user.id
    webapp_url = f"{WEB_APP_URL}?user_id={user_id}"
    keyboard = [[KeyboardButton("Открыть настройки", web_app=WebAppInfo(url=webapp_url))]]
    await context.bot.send_message(chat_id=update.effective_chat.id, text=STRINGS["greeting"])
   # await update.message.reply_text(
   #     STRINGS["greeting"],
   #     reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
   # )

start_handler = CommandHandler("start", start)
