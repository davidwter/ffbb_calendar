from datetime import datetime, timedelta
import pytz

PARIS_TZ = pytz.timezone('Europe/Paris')

def create_calendar(matches, calendar_name="Basketball Matches"):
    """
    Generates an ICS calendar from a list of matches.

    Args:
        matches (list): List of dictionaries containing match details.
                        Expected keys: 'start_time' (datetime), 'home_team', 'away_team', 'url'.
        calendar_name (str): Name of the calendar.

    Returns:
        str: The ICS calendar content as a string.
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//FFBB Calendar//FR",
        "X-WR-TIMEZONE:Europe/Paris",
    ]

    for match in matches:
        start_time = match['start_time']
        # Ensure it's in Paris timezone
        if start_time.tzinfo is None:
            start_time = PARIS_TZ.localize(start_time)
        else:
            start_time = start_time.astimezone(PARIS_TZ)

        end_time = start_time + timedelta(hours=2)

        # Format as local time (no Z suffix) - calendar apps will use X-WR-TIMEZONE
        dt_start = start_time.strftime("%Y%m%dT%H%M%S")
        dt_end = end_time.strftime("%Y%m%dT%H%M%S")

        # Generate a simple UID
        uid = f"{dt_start}-{hash(match['home_team'] + match['away_team']) & 0xffffffff}@ffbb"

        description_url = match.get('match_url') or match.get('url', '')

        lines.append("BEGIN:VEVENT")
        lines.append(f"DTSTART;TZID=Europe/Paris:{dt_start}")
        lines.append(f"DTEND;TZID=Europe/Paris:{dt_end}")
        lines.append(f"SUMMARY:{match['home_team']} vs {match['away_team']}")
        if description_url:
            lines.append(f"DESCRIPTION:Match details: {description_url}")
        lines.append(f"UID:{uid}")
        lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)
