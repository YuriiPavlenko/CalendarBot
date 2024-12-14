import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
TELEGRAM_WEBHOOK_URL = os.environ.get("TELEGRAM_WEBHOOK_URL", "https://example.com")
GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "23")
GOOGLE_SERVICE_ACCOUNT_KEY = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY", "fake_credentials")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "123")
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./test.db")
WEB_APP_URL = os.environ.get("WEB_APP_URL", "https://example.com")

WEBHOOK_PORT = 443
TIMEZONE_UA = "Europe/Kiev"
TIMEZONE_TH = "Asia/Bangkok"
