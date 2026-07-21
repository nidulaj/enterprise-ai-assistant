from typing import Any, Optional
from pydantic import BaseModel, Field

class AgentRequest(BaseModel):
    message: str = Field(description="The user's query or conversational message.")
    intent: str = Field(description="The detected intent name (e.g. SHOW_TASKS, CHAT).")
    payload: Optional[dict] = Field(default=None, description="Extracted parameters and data parsed from the user message.")
    model: str = Field(default="auto", description="Name of the model to use for completion.")

class AgentResponse(BaseModel):
    source: str = Field(description="The agent or service that handled the request (e.g. clickup, calendar, documents, ai).")
    response_text: str = Field(description="The final formatted message intended for the end-user (usually markdown).")
    data: Optional[dict] = Field(default=None, description="Optional raw structured data returned by tools for API or UI use.")
    model: str = Field(description="The LLM model used to process the response.")
