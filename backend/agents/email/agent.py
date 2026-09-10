from typing import Optional
from agents.base.agent import BaseAgent
from agents.base.models import (AgentRequest, AgentResponse)
from agents.base.context import AgentContext
from agents.base.tool import Tool
from agents.email.tools import send_email_tool

class EmailAgent(BaseAgent):
    
    name = "email"
    
    description = """
    Handles email communication,
    email drafting,
    meeting invitations,
    follow-ups,
    and status update emails.
    """
    
    capabilities = [
        "send email",
        "draft email",
        "compose email",
        "meeting invitation",
        "follow up email"
    ]
    
    def register_tools(self) -> None:
        self.tools_registry.register(Tool(
            name="send_email",
            description="Send an email to a recipient with a subject and body.",
            func=send_email_tool
        ), agent_name=self.name)
        
    def execute(self, request: AgentRequest, context: Optional[AgentContext] = None) -> AgentResponse:
        payload = request.payload or {}
        print("payload:", payload)
        
        to_email = payload.get("to_email") or payload.get("to") or payload.get("recipient")
        subject = payload.get("subject") or payload.get("title") or "No Subject"
        body = payload.get("body") or payload.get("content") or payload.get("message") or payload.get("text")
        
        # If 'body' was not provided, construct it dynamically from meeting parameters if present
        if not body:
            meeting_summary = payload.get("meeting_summary") or payload.get("summary") or "Meeting"
            meeting_link = payload.get("meeting_link") or payload.get("meet_link") or payload.get("link") or ""
            start_time = payload.get("meeting_start_time") or payload.get("start_time") or ""
            end_time = payload.get("meeting_end_time") or payload.get("end_time") or ""
            
            body_lines = [f"Here are the details for '{meeting_summary}':\n"]
            if start_time:
                body_lines.append(f"Time: {start_time}" + (f" to {end_time}" if end_time else ""))
            if meeting_link:
                body_lines.append(f"Meeting Link: {meeting_link}")
            
            body = "\n".join(body_lines) if len(body_lines) > 1 else request.message
        
        if not to_email:
            return AgentResponse(
                source=self.name,
                response_text="Failed to send email: Recipient email address ('to_email') is required.",
                data={"success": False, "error": "Recipient email address is required"},
                model=request.model
            )
            
        try:
            result = self.tools_registry.execute_tool(
                "send_email",
                to_email=to_email,
                subject=subject,
                body=body
            )
            response_text = result.get("message") or "Email sent successfully."
            data = result
        except Exception as e:
            response_text = f"Failed to send email: {str(e)}"
            data = {"success": False, "error": str(e)}
        
        return AgentResponse(
            source=self.name,
            response_text=response_text,
            data=data,
            model=request.model
        )