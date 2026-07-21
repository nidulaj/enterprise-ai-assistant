import re
import dateutil.parser
from datetime import datetime, time, timedelta
from google_calendar.calendar_service import CalendarService

def get_service():
    try:
        return CalendarService()
    except Exception as e:
        print("Warning: Google Calendar service failed to initialize:", str(e))
        return None

def parse_time_to_iso(time_str, default_offset_hours=0):
    if not time_str:
        return None
    time_str_clean = str(time_str).strip()
    now = datetime.now()
    target_date = now.date()

    if "tomorrow" in time_str_clean.lower():
        target_date = now.date() + timedelta(days=1)
        time_str_clean = re.sub(r"(?i)\btomorrow\b", "", time_str_clean).strip()

    base_default = datetime.combine(target_date, time(0, 0, 0)) + timedelta(hours=default_offset_hours)

    try:
        dt = dateutil.parser.parse(time_str_clean, default=base_default)
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        return time_str

def create_meeting(summary, start_time, end_time):
    """
    Creates a new meeting on Google Calendar.
    """
    service = get_service()
    if not service:
        return {"error": "Google Calendar service is not initialized"}
        
    if not summary:
        summary = "Sprint Review"
    if not start_time:
        start_time = "2pm"
    if not end_time:
        end_time = "3pm"
        
    iso_start = parse_time_to_iso(start_time, default_offset_hours=14)
    iso_end = parse_time_to_iso(end_time, default_offset_hours=15)

    try:
        meeting = service.create_meeting(
            summary=summary,
            start_time=iso_start,
            end_time=iso_end
        )
        return meeting
    except Exception as e:
        return {"error": str(e)}
