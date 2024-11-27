import datetime
import pytz

def format_meeting(event, thailand_tz, ukraine_tz):
    """Formats the event time for display in both Thailand and Ukraine time zones."""
    start_time = datetime.datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
    end_time = datetime.datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
    start_time_thailand = start_time.astimezone(thailand_tz).strftime('%H:%M')
    end_time_thailand = end_time.astimezone(thailand_tz).strftime('%H:%M')
    start_time_ukraine = start_time.astimezone(ukraine_tz).strftime('%H:%M')
    end_time_ukraine = end_time.astimezone(ukraine_tz).strftime('%H:%M')

    location = event.get('location', '')
    hangout_link = event.get('hangoutLink', '')

    location_info = f"Місце: {location}" if location else f"Посилання на зустріч: {hangout_link}" if hangout_link else ""

    return (
        f"*{event['summary']}*\n"
        f"Час у Таїланді: {start_time_thailand} - {end_time_thailand}\n"
        f"Час в Україні: {start_time_ukraine} - {end_time_ukraine}\n"
        f"{location_info}\n"
    ) 