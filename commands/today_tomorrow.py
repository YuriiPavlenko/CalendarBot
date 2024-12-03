import datetime
import pytz
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from calendar_service import get_calendar_meetings
from commands.settings import user_languages

def send_today_tomorrow_meetings(update: Update, context: CallbackContext):
    """Sends today's and tomorrow's meetings to the Telegram chat."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    language = user_languages.get(user_id, 'uk')  # Default to Ukrainian

    thailand_tz = pytz.timezone('Asia/Bangkok')
    ukraine_tz = pytz.timezone('Europe/Kiev')

    now = datetime.datetime.now(thailand_tz)
    start_of_today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_tomorrow = start_of_today + datetime.timedelta(days=2)

    today_meetings = []
    tomorrow_meetings = []

    meetings = get_calendar_meetings(start_of_today, end_of_tomorrow)

    for meeting in meetings:
        start_time = meeting.start
        if start_of_today <= start_time < start_of_today + datetime.timedelta(days=1):
            today_meetings.append(meeting)
        elif start_of_today + datetime.timedelta(days=1) <= start_time < end_of_tomorrow:
            tomorrow_meetings.append(meeting)

    if not today_meetings and not tomorrow_meetings:
        context.bot.send_message(chat_id=chat_id, text="No meetings found.")
    else:
        message = "Meetings for today:\n"
        for meeting in today_meetings:
            message += meeting.format(thailand_tz, ukraine_tz, language) + "\n"

        message += "\nMeetings for tomorrow:\n"
        for meeting in tomorrow_meetings:
            message += meeting.format(thailand_tz, ukraine_tz, language) + "\n"

        context.bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN) 