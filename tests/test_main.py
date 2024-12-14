import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from unittest.mock import Mock, patch, AsyncMock
from unittest.mock import Mock, patch, AsyncMock
from src.main import error_handler, startup
from telegram import Update, BotCommand
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
    # Set up mocks
    app = AsyncMock()
    app.bot = AsyncMock()
    app.job_queue = AsyncMock()
    app.job_queue.run_repeating = Mock()  # Change to regular Mock since we don't need to await this
    context = Mock(spec=ContextTypes.DEFAULT_TYPE)
    
    # Mock the jobs
    with patch('src.main.refresh_meetings') as mock_refresh, \
         patch('src.main.notification_job') as mock_notify:
        mock_refresh.return_value = None
        mock_notify.return_value = None
        
        async def post_init(app):
            await app.bot.set_my_commands([
                BotCommand("start", "Start the bot"),
                BotCommand("get_today", "Get today's meetings"),
                BotCommand("get_tomorrow", "Get tomorrow's meetings"),
                BotCommand("get_rest_week", "Get the rest of the week's meetings"),
                BotCommand("get_next_week", "Get next week's meetings"),
            ])
            await startup(app)
            
            # Get and call the job callbacks
            refresh_callback = app.job_queue.run_repeating.call_args_list[0][0][0]
            notify_callback = app.job_queue.run_repeating.call_args_list[1][0][0]
            
            # Mock the callback executions
            if asyncio.iscoroutinefunction(refresh_callback):
                await refresh_callback()
            if asyncio.iscoroutinefunction(notify_callback):
                await notify_callback(context)
        
        app.post_init = post_init
        await app.post_init(app)
        
        # Verify calls
        app.bot.set_my_commands.assert_called_once()
        assert app.job_queue.run_repeating.call_count == 2
        assert mock_refresh.called
        assert mock_notify.called

@pytest.mark.asyncio
async def test_startup_error():
    app = Mock()
    app.bot = AsyncMock()
    app.bot.set_my_commands.side_effect = Exception("Test error")
    await startup(app)  # Should handle error gracefully
