from typing import Optional
from agents.base.agent import BaseAgent
from agents.base.models import AgentRequest, AgentResponse
from agents.base.context import AgentContext
from agents.base.tool import Tool
from agents.calendar.tools import create_meeting

class CalendarAgent(BaseAgent):
    name = "calendar"
    description = "Handles Google Calendar scheduling, event creation, and booking meetings."
    capabilities = [
        "Schedule Google Calendar meetings",
        "Create calendar events with summary, start time, and end time",
        "Generate video call / Google Meet links"
    ]

    def register_tools(self) -> None:
        self.tools_registry.register(Tool(
            name="create_meeting",
            description="Create a new calendar event with summary, start time, and end time.",
            func=create_meeting
        ), agent_name=self.name)

    def execute(self, request: AgentRequest, context: Optional[AgentContext] = None) -> AgentResponse:
        payload = request.payload or {}
        summary = payload.get("summary") or payload.get("title") or "Sprint Review"
        start_time = payload.get("start_time") or "2026-07-14T15:00:00"
        end_time = payload.get("end_time") or "2026-07-14T16:00:00"

        meeting = self.tools_registry.execute_tool(
            "create_meeting",
            summary=summary,
            start_time=start_time,
            end_time=end_time
        )

        if isinstance(meeting, dict) and "error" in meeting:
            response_text = f"Failed to create meeting: {meeting['error']}"
        elif isinstance(meeting, dict):
            response_text = (
                f"Meeting created successfully.\n\n"
                f"Event: {meeting.get('summary', summary)}\n"
                f"Time: {meeting.get('start_time', start_time)} to {meeting.get('end_time', end_time)}\n"
                f"Link: {meeting.get('meet_link') or 'No link generated'}"
            )
        else:
            response_text = str(meeting)

        return AgentResponse(
            source=self.name,
            response_text=response_text,
            data=meeting if isinstance(meeting, dict) else {"result": meeting},
            model=request.model
        )
