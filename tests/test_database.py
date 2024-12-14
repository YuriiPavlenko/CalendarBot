import pytest
from database import (  # Updated import path
    get_user_settings,
    set_filter,
    set_notifications,
    set_user_info,
    UserSettings,
    Meeting,
    SessionLocal
)

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

def test_get_user_settings_new_user(db_session):
    user_id = 12345
    settings = get_user_settings(db_session, user_id)
    assert settings.user_id == user_id
    assert settings.filter_by_attendant is False
    assert settings.notify_1h is False
    assert settings.notify_15m is False
    assert settings.notify_5m is False
    assert settings.notify_new is False

def test_get_user_settings_existing_user(db_session):
    user_id = 12346
    settings = UserSettings(user_id=user_id, notify_1h=True)
    db_session.add(settings)
    db_session.commit()

    retrieved = get_user_settings(db_session, user_id)
    assert retrieved.user_id == user_id
    assert retrieved.notify_1h is True

def test_set_filter(db_session):
    user_id = 12347
    set_filter(db_session, user_id, True)
    settings = get_user_settings(db_session, user_id)
    assert settings.filter_by_attendant is True

    set_filter(db_session, user_id, False)
    settings = get_user_settings(db_session, user_id)
    assert settings.filter_by_attendant is False

def test_set_notifications(db_session):
    user_id = 12348
    set_notifications(db_session, user_id, True, True, True, True)
    settings = get_user_settings(db_session, user_id)
    assert settings.notify_1h is True
    assert settings.notify_15m is True
    assert settings.notify_5m is True
    assert settings.notify_new is True

def test_set_user_info(db_session):
    user_id = 12349
    username = "@testuser"
    fullname = "Test User"
    set_user_info(db_session, user_id, username, fullname)
    settings = get_user_settings(db_session, user_id)
    assert settings.username == username
    assert settings.fullname == fullname
