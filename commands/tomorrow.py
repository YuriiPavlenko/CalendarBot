import datetime
import pytz
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from calendar_service import get_calendar_meetings
from commands.settings import get_user_language
from localization import get_texts

def send_tomorrow_meetings(update: Update, context: CallbackContext):
    """Sends tomorrow's meetings to the Telegram chat."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    language = get_user_language(user_id)
    texts = get_texts(language)

    thailand_tz = pytz.timezone('Asia/Bangkok')
    ukraine_tz = pytz.timezone('Europe/Kiev')

    now = datetime.datetime.now(thailand_tz)
    start_of_tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    end_of_tomorrow = start_of_tomorrow + datetime.timedelta(days=1)

    tomorrow_meetings = get_calendar_meetings(start_of_tomorrow, end_of_tomorrow)

    message = f"*{texts['meetings_tomorrow'].strip().upper()}*\n\n"
    if not tomorrow_meetings:
        message += texts['no_meetings']
    else:
        for meeting in tomorrow_meetings:
            message += meeting.format(thailand_tz, ukraine_tz, language) + "\n"

    context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN) 