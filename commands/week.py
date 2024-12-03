import datetime
import pytz
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from calendar_service import get_calendar_meetings
from commands.settings import get_user_language

def send_week_meetings(update: Update, context: CallbackContext):
    """Sends all meetings for the current week to the Telegram chat."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    language = get_user_language(user_id)

    thailand_tz = pytz.timezone('Asia/Bangkok')
    ukraine_tz = pytz.timezone('Europe/Kiev')

    now = datetime.datetime.now(thailand_tz)
    start_of_week = now - datetime.timedelta(days=now.weekday())  # Start of the week (Monday)
    end_of_week = start_of_week + datetime.timedelta(days=7)  # End of the week (Sunday)

    meetings = get_calendar_meetings(start_of_week, end_of_week)

    # Language-specific text
    texts = {
        'uk': {
            'no_meetings': "Немає зустрічей.",
            'header': "Зустрічі на цей тиждень:\n",
            'days_of_week': ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П’ятниця', 'Субота', 'Неділя']
        },
        'ru': {
            'no_meetings': "Нет встреч.",
            'header': "Встречи на эту неделю:\n",
            'days_of_week': ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        },
        'en': {
            'no_meetings': "No meetings found.",
            'header': "Meetings for this week:\n",
            'days_of_week': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        },
        'th': {
            'no_meetings': "ไม่พบการประชุม",
            'header': "การประชุมสำหรับสัปดาห์นี้:\n",
            'days_of_week': ['วันจันทร์', 'วันอังคาร', 'วันพุธ', 'วันพฤหัสบดี', 'วันศุกร์', 'วันเสาร์', 'วันอาทิตย์']
        }
    }

    text = texts[language]

    if not meetings:
        context.bot.send_message(chat_id=chat_id, text=text['no_meetings'])
    else:
        message = text['header']
        current_day = None

        for meeting in meetings:
            meeting_day = meeting.start.astimezone(thailand_tz).weekday()

            if current_day != meeting_day:
                current_day = meeting_day
                message += f"\n*{text['days_of_week'][current_day]}*\n"

            message += meeting.format(thailand_tz, ukraine_tz, language) + "\n"

        context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN) 