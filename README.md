# Telegram Meetings Bot

This Telegram bot interacts with a Google Calendar to show users scheduled meetings, filter them by their attendance, 
and send notifications before meetings. It also allows users to set their filter and notification preferences.

## Features
- Language: Russian
- Fetches meetings from Google Calendar
- Filter settings: show all or only user's meetings
- Notification settings: 
  - 1 hour before meeting
  - 15 minutes before meeting
  - 5 minutes before meeting
  - On new meeting creation
- Commands:
  - /start
  - /settings_filter
  - /settings_notifications
  - /get_today
  - /get_tomorrow
  - /get_rest_week
  - /get_next_week
- Menu button to show available commands
- Uses webhook to receive Telegram updates
- Logging of all requests, responses, and errors
- User settings stored in a database (SQLite)

## Environment Variables
- GOOGLE_CALENDAR_ID
- GOOGLE_SERVICE_ACCOUNT_KEY (JSON string of the service account credentials)
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- TELEGRAM_WEBHOOK_URL

## Deployment
This project is ready to be deployed on Railway. Make sure to set the environment variables 
and point Telegram's webhook to TELEGRAM_WEBHOOK_URL.

## Installation
