# Telegram Meeting Bot

This is a Telegram bot designed to manage meetings using Google Calendar. It allows users to view meetings, create new meetings, and manage notifications for upcoming meetings.

## Features

- **Language Support**: Users can choose between Russian and Ukrainian.
- **Meeting Management**: View meetings for today, tomorrow, or the week. Create new meetings with optional details.
- **User-Specific Meetings**: Filter meetings where the user is a participant.
- **Notifications**: Subscribe to notifications for meetings at various intervals.

## Setup

### Prerequisites

- Python 3.7+
- Google Cloud account with a service account for Google Calendar API
- Telegram Bot Token

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/telegram-meeting-bot.git
   cd telegram-meeting-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Set the following environment variables in your deployment platform (e.g., Railway):
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token.
   - `GOOGLE_APPLICATION_CREDENTIALS`: Path to your Google service account JSON file.

4. **Run the Bot**:
   Deploy the bot on your preferred platform (e.g., Railway) and start the bot.

## Usage

- **/start**: Start interacting with the bot and choose your language.
- **/show_meetings**: View all meetings for today.
- **/show_user_meetings**: View meetings where you are a participant.
- **/manage_notifications**: Manage your notification preferences.
- **/subscribe_notifications**: Subscribe to meeting notifications.
- **/unsubscribe_notifications**: Unsubscribe from meeting notifications.
- **/create_meeting**: Create a new meeting.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
