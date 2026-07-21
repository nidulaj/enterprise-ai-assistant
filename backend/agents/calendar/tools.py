from google_calendar.calendar_service import CalendarService

def get_service():
    try:
        return CalendarService()
    except Exception as e:
        print("Warning: Google Calendar service failed to initialize:", str(e))
        return None

def create_meeting(summary, start_time, end_time):
    """
    Creates a new meeting on Google Calendar.
    """
    service = get_service()
    if not service:
        return {"error": "Google Calendar service is not initialized"}
        
    if not summary:
        return {"error": "Summary is required"}
    if not start_time:
        return {"error": "Start time is required"}
    if not end_time:
        return {"error": "End time is required"}
        
    try:
        meeting = service.create_meeting(
            summary=summary,
            start_time=start_time,
            end_time=end_time
        )
        return meeting
    except Exception as e:
        return {"error": str(e)}
