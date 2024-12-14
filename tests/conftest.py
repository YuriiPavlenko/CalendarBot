import pytest
import asyncio
import os

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(autouse=True)
def env_setup():
    """Configure environment variables for testing."""
    original_db_url = os.environ.get('DATABASE_URL')
    os.environ['TESTING'] = '1'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    yield
    if original_db_url:
        os.environ['DATABASE_URL'] = original_db_url
    else:
        del os.environ['DATABASE_URL']
    del os.environ['TESTING']
