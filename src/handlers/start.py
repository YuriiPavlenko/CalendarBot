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
    keyboard = [[KeyboardButton(text="Открыть настройки", web_app=WebAppInfo(url=webapp_url))]]
    await update.message.reply_text(text=STRINGS["greeting"], reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True), parse_mode='MarkdownV2')
    

start_handler = CommandHandler("start", start)
