import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.main import error_handler, startup
from telegram import Update
from telegram.ext import ContextTypes

@pytest.fixture
def mock_update():
    update = Mock(spec=Update)
    update.effective_message = Mock()
    update.effective_chat = Mock()
    update.effective_chat.id = 123456789
    return update

@pytest.fixture
def mock_context():
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot = AsyncMock()
    return context

@pytest.mark.asyncio
async def test_error_handler(mock_update, mock_context):
    mock_context.error = Exception("Test error")
    await error_handler(mock_update, mock_context)
    # Should not raise any exceptions

@pytest.mark.asyncio
async def test_startup():
    app = AsyncMock()
    app.bot = AsyncMock()
    
    async def post_init(app):
        await app.bot.set_my_commands([
            BotCommand("start", "Start the bot"),
            BotCommand("get_today", "Get today's meetings"),
            BotCommand("get_tomorrow", "Get tomorrow's meetings"),
            BotCommand("get_rest_week", "Get the rest of the week's meetings"),
            BotCommand("get_next_week", "Get next week's meetings"),
        ])
        await startup(app)
    
    app.post_init = post_init
    await app.post_init(app)
    app.bot.set_my_commands.assert_called_once()
        await app.bot.set_my_commands([
            BotCommand("start", "Start the bot"),
            BotCommand("get_today", "Get today's meetings"),
            BotCommand("get_tomorrow", "Get tomorrow's meetings"),
            BotCommand("get_rest_week", "Get the rest of the week's meetings"),
            BotCommand("get_next_week", "Get next week's meetings"),
        ])
        await startup(app)
    
    app.post_init = post_init
    await app.post_init(app)
    app.bot.set_my_commands.assert_called_once()

@pytest.mark.asyncio
async def test_startup_error():
    app = Mock()
    app.bot = AsyncMock()
    app.bot.set_my_commands.side_effect = Exception("Test error")
    await startup(app)  # Should handle error gracefully
