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

def parse_meeting_times(start_input=None, end_input=None, default_duration_hours=1):
    """
    Robustly parses natural language or ISO date/time strings into valid RFC 3339 / ISO format strings.
    Handles ranges ('2pm - 3pm'), relative dates ('today', 'tomorrow', 'Friday'), noise words,
    and guarantees end_time > start_time.
    """
    now = datetime.now()

    # 1. Handle case where start_input contains both start and end, e.g. "2pm - 3pm" or "10am to 11am"
    if start_input and not end_input:
        range_match = re.search(r"^(.*?)\s*(?:-|\bto\b|\buntil\b)\s*(.*?)$", str(start_input).strip(), re.IGNORECASE)
        if range_match:
            potential_start, potential_end = range_match.groups()
            if re.search(r"\d", potential_end):
                start_input = potential_start
                end_input = potential_end

    start_str = str(start_input).strip() if start_input else ""
    end_str = str(end_input).strip() if end_input else ""

    # Determine base target date
    target_date = now.date()
    lower_start = start_str.lower()

    if "day after tomorrow" in lower_start:
        target_date = now.date() + timedelta(days=2)
        start_str = re.sub(r"(?i)\bday after tomorrow\b", "", start_str).strip()
    elif "tomorrow" in lower_start:
        target_date = now.date() + timedelta(days=1)
        start_str = re.sub(r"(?i)\btomorrow\b", "", start_str).strip()
    elif "today" in lower_start:
        target_date = now.date()
        start_str = re.sub(r"(?i)\btoday\b", "", start_str).strip()
    else:
        # Check weekdays (e.g. next monday, friday)
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for idx, day_name in enumerate(weekdays):
            if day_name in lower_start:
                current_weekday = now.weekday()
                days_ahead = (idx - current_weekday) % 7
                if "next" in lower_start or days_ahead == 0:
                    days_ahead += 7
                target_date = now.date() + timedelta(days=days_ahead)
                start_str = re.sub(rf"(?i)\b(next\s+)?{day_name}\b", "", start_str).strip()
                break

    # Clean leading noise words like "at", "on", "from"
    start_str = re.sub(r"^(at|on|from|around)\s+", "", start_str, flags=re.IGNORECASE).strip()

    # Default time: next hour or 10:00 AM
    default_start_hour = (now.hour + 1) if target_date == now.date() and now.hour < 23 else 10
    base_start_dt = datetime.combine(target_date, time(default_start_hour, 0, 0))

    if not start_str:
        start_dt = base_start_dt
    else:
        try:
            start_dt = dateutil.parser.parse(start_str, default=base_start_dt, fuzzy=True)
            if target_date != now.date() and start_dt.date() == now.date():
                start_dt = datetime.combine(target_date, start_dt.time())
        except Exception:
            start_dt = base_start_dt

    # Parse end_dt
    if not end_str:
        end_dt = start_dt + timedelta(hours=default_duration_hours)
    else:
        lower_end = end_str.lower()
        end_target_date = start_dt.date()
        if "tomorrow" in lower_end:
            end_target_date = now.date() + timedelta(days=1)
            end_str = re.sub(r"(?i)\btomorrow\b", "", end_str).strip()
        end_str = re.sub(r"^(at|to|until|around)\s+", "", end_str, flags=re.IGNORECASE).strip()

        base_end_dt = start_dt + timedelta(hours=default_duration_hours)
        if not end_str:
            end_dt = base_end_dt
        else:
            try:
                end_dt = dateutil.parser.parse(end_str, default=datetime.combine(end_target_date, time(0, 0, 0)), fuzzy=True)
                if end_target_date != now.date() and end_dt.date() == now.date():
                    end_dt = datetime.combine(end_target_date, end_dt.time())
            except Exception:
                end_dt = base_end_dt

    # Ensure end_dt is strictly after start_dt
    if end_dt <= start_dt:
        end_dt = start_dt + timedelta(hours=default_duration_hours)

    return start_dt.strftime("%Y-%m-%dT%H:%M:%S"), end_dt.strftime("%Y-%m-%dT%H:%M:%S")


def parse_time_to_iso(time_str, default_offset_hours=0):
    """
    Backward-compatible single timestamp parser.
    """
    if not time_str:
        return None
    iso_start, _ = parse_meeting_times(start_input=time_str, default_duration_hours=1)
    return iso_start


def create_meeting(summary=None, start_time=None, end_time=None):
    """
    Creates a new meeting on Google Calendar with parsed and validated ISO dates.
    """
    service = get_service()
    if not service:
        return {"error": "Google Calendar service is not initialized"}
        
    if not summary or not str(summary).strip():
        summary = "Meeting"
        
    iso_start, iso_end = parse_meeting_times(start_input=start_time, end_input=end_time)

    try:
        meeting = service.create_meeting(
            summary=summary,
            start_time=iso_start,
            end_time=iso_end
        )
        return meeting
    except Exception as e:
        return {"error": str(e)}
