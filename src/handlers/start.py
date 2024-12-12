import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes, CommandHandler
from ..database import SessionLocal, set_user_info
from ..localization import STRINGS
from ..config import WEB_APP_URL

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = f"@{update.effective_user.username}" if update.effective_user.username else None
    fullname = update.effective_user.full_name

    session = SessionLocal()
    set_user_info(session, user_id, username, fullname)
    session.close()

    text = '\n'.join([STRINGS["greeting"], STRINGS["menu_title"], STRINGS["menu_start"],STRINGS["menu_get_today"],STRINGS["menu_get_tomorrow"],STRINGS["menu_get_rest_week"],STRINGS["menu_get_next_week"]])
    webapp_url = f"{WEB_APP_URL}?user_id={user_id}"
    keyboard = [[KeyboardButton("Открыть мини-приложение", web_app=WebAppInfo(url=webapp_url))]]
    await update.message.reply_text(text=text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

start_handler = CommandHandler("start", start)
