from telegram import Update
from telegram.ext import CallbackContext
from utils.google_calendar import create_calendar_event
from utils.localization import get_texts
from utils.database import Session, User

def create_meeting(update: Update, context: CallbackContext):
    """Create a new meeting."""
    user_id = update.effective_user.id
    session = Session()
    user = session.query(User).filter_by(telegram_id=user_id).first()
    texts = get_texts(user.language)

    # Collect meeting details from user
    update.message.reply_text(texts['enter_meeting_title'])
    title = context.bot.wait_for_message(chat_id=update.effective_chat.id).text

    update.message.reply_text(texts['enter_meeting_start_time'])
    start_time = context.bot.wait_for_message(chat_id=update.effective_chat.id).text

    update.message.reply_text(texts['enter_meeting_end_time'])
    end_time = context.bot.wait_for_message(chat_id=update.effective_chat.id).text

    # Optional details
    update.message.reply_text(texts['enter_meeting_location'])
    location = context.bot.wait_for_message(chat_id=update.effective_chat.id).text

    update.message.reply_text(texts['enter_meeting_attendees'])
    attendees = context.bot.wait_for_message(chat_id=update.effective_chat.id).text.split(',')

    # Create the meeting
    event = create_calendar_event(title, start_time, end_time, location, attendees)
    if event:
        update.message.reply_text(texts['meeting_created'])
    else:
        update.message.reply_text(texts['meeting_creation_failed'])
