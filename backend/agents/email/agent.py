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
        
        to_email = payload.get("to_email") or payload.get("to") or payload.get("recipient")
        subject = payload.get("subject") or payload.get("title") or "No Subject"
        body = payload.get("body") or payload.get("content") or payload.get("message") or ""
        
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