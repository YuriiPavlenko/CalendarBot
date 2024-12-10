import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_WEBHOOK_URL = os.environ.get("TELEGRAM_WEBHOOK_URL")
GOOGLE_CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID")
GOOGLE_SERVICE_ACCOUNT_KEY = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Webhook settings
WEBHOOK_HOST = TELEGRAM_WEBHOOK_URL
WEBHOOK_PORT = 443

# Use the Railway volume at /app/data
DATABASE_URL = "sqlite:////app/data/database.db"

TIMEZONE_UA = "Europe/Kiev"
TIMEZONE_TH = "Asia/Bangkok"
