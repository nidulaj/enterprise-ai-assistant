from flask import Blueprint
from flask import jsonify

from google_calendar.calendar_service import CalendarService

calendar_bp = Blueprint(
    "calendar",
    __name__
)

calendar = CalendarService()


@calendar_bp.route(
    "/calendar/test",
    methods=["GET"]
)
def create_test_meeting():

    meeting = calendar.create_meeting(

        summary="Sprint Review",

        start_time="2026-07-10T15:00:00",

        end_time="2026-07-10T16:00:00"

    )

    return jsonify(meeting)