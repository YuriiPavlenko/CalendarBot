from telegram import Update
from telegram.ext import CallbackContext
from utils.database import Session, Subscription
from utils.localization import get_texts
from utils.database import User

def manage_notifications(update: Update, context: CallbackContext):
    """Manage user notifications."""
    session = Session()
    user_id = update.effective_user.id
    user = session.query(User).filter_by(telegram_id=user_id).first()
    texts = get_texts(user.language)

    # Display current notification settings
    subscription = session.query(Subscription).filter_by(user_id=user.id).first()
    if not subscription:
        subscription = Subscription(user_id=user.id)
        session.add(subscription)
        session.commit()

    update.message.reply_text(
        f"{texts['current_notifications']}\n"
        f"{texts['notify_day_before']}: {subscription.notify_day_before}\n"
        f"{texts['notify_hour_before']}: {subscription.notify_hour_before}\n"
        f"{texts['notify_five_minutes_before']}: {subscription.notify_five_minutes_before}"
    )

def subscribe_notifications(update: Update, context: CallbackContext):
    """Subscribe to notifications."""
    session = Session()
    user_id = update.effective_user.id
    user = session.query(User).filter_by(telegram_id=user_id).first()
    texts = get_texts(user.language)

    # Update subscription settings
    subscription = session.query(Subscription).filter_by(user_id=user.id).first()
    if not subscription:
        subscription = Subscription(user_id=user.id)
        session.add(subscription)

    # Example: Subscribe to all notifications
    subscription.notify_day_before = True
    subscription.notify_hour_before = True
    subscription.notify_five_minutes_before = True
    session.commit()

    update.message.reply_text(texts['subscribed_notifications'])

def unsubscribe_notifications(update: Update, context: CallbackContext):
    """Unsubscribe from notifications."""
    session = Session()
    user_id = update.effective_user.id
    user = session.query(User).filter_by(telegram_id=user_id).first()
    texts = get_texts(user.language)

    # Update subscription settings
    subscription = session.query(Subscription).filter_by(user_id=user.id).first()
    if subscription:
        subscription.notify_day_before = False
        subscription.notify_hour_before = False
        subscription.notify_five_minutes_before = False
        session.commit()

    update.message.reply_text(texts['unsubscribed_notifications'])
