from agents.base.agent import BaseAgent
from agents.base.models import (AgentRequest, AgentResponse)

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
    
    def register_tools(self):
        self.tools_registry.register_tool(
            "send_email",
            send_email_tool,
            self.name
        )
        
    def execute(self, request: AgentRequest, context)-> AgentResponse:
        payload = request.payload
        
        result = self.tools_registry.execute_tool(
            "send_email",
            to_email=payload["to_email"],
            subject=payload["subject"],
            body=payload["body"]
        )
        
        return AgentResponse(
            source="email",
            response_text=result["message"],
            data=result
        )