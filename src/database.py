from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL

Base = declarative_base()

class UserSettings(Base):
    __tablename__ = "user_settings"
    user_id = Column(Integer, primary_key=True)
    filter_type = Column(String, default="all")
    notify_1h = Column(Boolean, default=False)
    notify_15m = Column(Boolean, default=False)
    notify_5m = Column(Boolean, default=False)
    notify_new = Column(Boolean, default=False)
    username = Column(String, nullable=True)
    fullname = Column(String, nullable=True)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_user_settings(session, user_id):
    us = session.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not us:
        us = UserSettings(user_id=user_id)
        session.add(us)
        session.commit()
    return us

def set_filter(session, user_id, filter_type):
    us = get_user_settings(session, user_id)
    us.filter_type = filter_type
    session.commit()

def set_notifications(session, user_id, n1h, n15m, n5m, nnew):
    us = get_user_settings(session, user_id)
    us.notify_1h = n1h
    us.notify_15m = n15m
    us.notify_5m = n5m
    us.notify_new = nnew
    session.commit()

def set_user_info(session, user_id, username, fullname):
    us = get_user_settings(session, user_id)
    us.username = username
    us.fullname = fullname
    session.commit()
