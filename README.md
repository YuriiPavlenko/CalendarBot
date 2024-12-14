# Telegram Meetings Bot with Mini-app

This Telegram bot interacts with Google Calendar to show and filter meetings, and manage notifications.  
User settings are edited via a Telegram WebApp (mini-app) with radio/checkbox inputs.

## Features
- Language: Russian
- Fetch & cache meetings from Google Calendar
- Filter: all or only user’s meetings
- Notifications: 1h, 15m, 5m before meeting, and new meeting
- Mini-app for settings and viewing meetings
- Uses PostgreSQL for settings storage
- Sends notifications on new or updated meetings

## Setup
1. Set environment variables:
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_WEBHOOK_URL
   - GOOGLE_CALENDAR_ID
   - GOOGLE_SERVICE_ACCOUNT_KEY (JSON as a string)
   - DATABASE_URL (e.g. `postgresql+psycopg2://user:pass@host:port/db`)
   - WEB_APP_URL (URL where Flask mini-app is hosted)
2. `pip install -r requirements.txt`
3. Run `python src/main.py` for the bot, `python web_app/app.py` for the mini-app.
4. Set Telegram webhook to TELEGRAM_WEBHOOK_URL.

## Logging
Logs are in JSON format for Railway compatibility.
# Trigger CI
