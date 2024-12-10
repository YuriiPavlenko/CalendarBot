import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_WEBHOOK_URL = os.environ.get("TELEGRAM_WEBHOOK_URL")
GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID")
GOOGLE_SERVICE_ACCOUNT_KEY = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Webhook settings
WEBHOOK_HOST = TELEGRAM_WEBHOOK_URL
WEBHOOK_PORT = 443

# Use the DATABASE_URL provided by Railway for PostgreSQL
# Format: postgresql+psycopg2://user:password@host:port/dbname
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+psycopg2://user:pass@localhost:5432/mydb")

TIMEZONE_UA = "Europe/Kiev"
TIMEZONE_TH = "Asia/Bangkok"
