from telegram import Update
from telegram.ext import CallbackContext
from utils.google_calendar import get_meetings_for_period
from utils.database import Session, User
from utils.localization import get_texts

def show_meetings(update: Update, context: CallbackContext):
    """Shows all meetings for a specified period."""
    session = Session()
    user_id = update.effective_user.id
    user = session.query(User).filter_by(telegram_id=user_id).first()
    texts = get_texts(user.language)

    # Fetch meetings for today
    meetings = get_meetings_for_period('today')  # Replace 'today' with actual logic

    if not meetings:
        update.message.reply_text(texts['no_meetings'])
    else:
        for meeting in meetings:
            update.message.reply_text(format_meeting(meeting, texts))

def show_user_meetings(update: Update, context: CallbackContext):
    """Shows meetings where the user is a participant."""
    session = Session()
    user_id = update.effective_user.id
    user = session.query(User).filter_by(telegram_id=user_id).first()
    texts = get_texts(user.language)

    # Fetch meetings for today
    meetings = get_meetings_for_period('today', user.username)  # Pass username to filter

    if not meetings:
        update.message.reply_text(texts['no_user_meetings'])
    else:
        for meeting in meetings:
            update.message.reply_text(format_meeting(meeting, texts))

def format_meeting(meeting, texts):
    """Formats meeting details for display."""
    return (
        f"{texts['meeting_title']}: {meeting['title']}\n"
        f"{texts['meeting_time']}: {meeting['start_time']} - {meeting['end_time']}\n"
        f"{texts['meeting_location']}: {meeting.get('location', texts['no_location'])}\n"
        f"{texts['meeting_attendees']}: {', '.join(meeting.get('attendees', []))}"
    )
