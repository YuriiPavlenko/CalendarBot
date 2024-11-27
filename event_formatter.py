import datetime
import pytz

def format_meeting(meeting, thailand_tz, ukraine_tz):
    """
    Formats a meeting's details into a string.
    """
    start_time = datetime.datetime.fromisoformat(meeting['start']['dateTime'])
    end_time = datetime.datetime.fromisoformat(meeting['end']['dateTime'])

    start_time_thailand = start_time.astimezone(thailand_tz).strftime('%H:%M')
    end_time_thailand = end_time.astimezone(thailand_tz).strftime('%H:%M')
    start_time_ukraine = start_time.astimezone(ukraine_tz).strftime('%H:%M')
    end_time_ukraine = end_time.astimezone(ukraine_tz).strftime('%H:%M')

    formatted_meeting = (
        f"*{meeting['summary']}*\n"
        f"Час у Таїланді: {start_time_thailand} - {end_time_thailand}\n"
        f"Час в Україні: {start_time_ukraine} - {end_time_ukraine}\n"
        f"Мета: {meeting['goal']}\n"
        f"Учасники: {', '.join(meeting['attendants']) if meeting['attendants'] else 'Немає учасників'}\n"
    )
    return formatted_meeting 