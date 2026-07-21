from flask import Blueprint
from flask import jsonify

from google_calendar.calendar_service import CalendarService

calendar_bp = Blueprint(
    "calendar",
    __name__
)


@calendar_bp.route(
    "/calendar/test",
    methods=["GET"]
)
def create_test_meeting():
    try:
        calendar = CalendarService()
        meeting = calendar.create_meeting(
            summary="Sprint Review",
            start_time="2026-07-14T15:00:00",
            end_time="2026-07-14T16:00:00"
        )
        return jsonify(meeting)
    except Exception as e:
        return jsonify({"error": str(e)}), 500