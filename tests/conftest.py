import pytest
import asyncio
import os
from unittest.mock import patch

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def env_setup():
    """Configure environment variables for testing."""
    os.environ['TESTING'] = '1'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    yield
    del os.environ['TESTING']
    del os.environ['DATABASE_URL']

@pytest.fixture(autouse=True)
def mock_database():
    with patch('database.DATABASE_URL', 'sqlite:///:memory:'):
        yield
