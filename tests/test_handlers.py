import pytest
from unittest.mock import Mock, patch, AsyncMock
from telegram import Update, Chat, Message, User, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from datetime import datetime, timezone
from src.gets import _get_meetings_for_period
from src.start import start

@pytest.fixture
def update():
    update = Mock(spec=Update)
    update.effective_chat = Mock(spec=Chat)
    update.effective_chat.id = 12345
    update.message = Mock(spec=Message)
    update.effective_user = Mock(spec=User)
    update.effective_user.id = 12345
    return update

@pytest.fixture
def context():
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = AsyncMock()
    return context

@pytest.fixture
def mock_dates():
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    end = datetime(2024, 1, 2, tzinfo=timezone.utc)
    return (start, end)

@pytest.mark.asyncio
async def test_start_command(update, context):
    with patch('src.start.SessionLocal') as mock_session, \
         patch('src.start.set_user_info') as mock_set_user:
        mock_session.return_value = Mock(query=Mock(return_value=Mock(all=Mock(return_value=[]))))
        await start(update, context)
        update.message.reply_text.assert_called_once()
        args, kwargs = update.message.reply_text.call_args
        assert isinstance(kwargs['reply_markup'], ReplyKeyboardMarkup)

@pytest.mark.asyncio
async def test_today_command(update, context, mock_dates):
    with patch('src.gets.SessionLocal') as mock_session, \
         patch('src.gets.get_today_th') as mock_get_today:
        mock_session.return_value = Mock()
        mock_session.return_value.query.return_value.filter.return_value.all.return_value = []
        mock_get_today.return_value = mock_dates
        await _get_meetings_for_period(update, context, "today")
        update.message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_tomorrow_command(update, context, mock_dates):
    with patch('src.gets.SessionLocal') as mock_session, \
         patch('src.gets.get_tomorrow_th') as mock_get_tomorrow:
        mock_session.return_value = Mock()
        mock_session.return_value.query.return_value.filter.return_value.all.return_value = []
        mock_get_tomorrow.return_value = mock_dates
        await _get_meetings_for_period(update, context, "tomorrow")
        update.message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_week_command(update, context, mock_dates):
    with patch('src.gets.SessionLocal') as mock_session, \
         patch('src.gets.get_rest_week_th') as mock_get_week:
        mock_session.return_value = Mock()
        mock_session.return_value.query.return_value.filter.return_value.all.return_value = []
        mock_get_week.return_value = mock_dates
        await _get_meetings_for_period(update, context, "rest_week")
        update.message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_next_week_command(update, context, mock_dates):
    with patch('src.gets.SessionLocal') as mock_session, \
         patch('src.gets.get_next_week_th') as mock_get_next_week:
        mock_session.return_value = Mock()
        mock_session.return_value.query.return_value.filter.return_value.all.return_value = []
        mock_get_next_week.return_value = mock_dates
        await _get_meetings_for_period(update, context, "next_week")
        update.message.reply_text.assert_called_once()
