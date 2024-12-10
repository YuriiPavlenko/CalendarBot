from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
from ..database import SessionLocal, set_filter
from ..localization import STRINGS

FILTER_ONLY = 10

async def settings_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(STRINGS["settings_filter_all"], callback_data="all"),
         InlineKeyboardButton(STRINGS["settings_filter_mine"], callback_data="mine")]
    ]
    await update.message.reply_text(STRINGS["settings_filter_intro"],
                                    reply_markup=InlineKeyboardMarkup(keyboard))
    context.user_data["from_start"] = False
    return FILTER_ONLY

async def settings_filter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    choice = query.data
    session = SessionLocal()
    set_filter(session, user_id, choice)
    session.close()
    await query.edit_message_text(text=STRINGS["settings_filter_saved"])
    await query.message.reply_text(STRINGS["filter_saved_standalone"])
    return ConversationHandler.END

filter_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("settings_filter", settings_filter)],
    states={
        FILTER_ONLY: [CallbackQueryHandler(settings_filter_callback)]
    },
    fallbacks=[],
    name="filter_conv",
    persistent=False,
    per_message=True
)
