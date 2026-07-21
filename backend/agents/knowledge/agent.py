from typing import Optional
from agents.base.agent import BaseAgent
from agents.base.models import AgentRequest, AgentResponse
from agents.base.context import AgentContext
from agents.base.tool import Tool
from agents.knowledge.tools import (
    search_documents,
    answer_question,
    get_documents,
)

class KnowledgeAgent(BaseAgent):
    name = "knowledge"
    description = "Handles document search, questions about uploaded documents (RAG), and lists uploaded files."
    capabilities = [
        "Search uploaded PDF documents",
        "Answer questions using company knowledge base (RAG)",
        "List uploaded document files and metadata"
    ]

    def register_tools(self) -> None:
        self.tools_registry.register(Tool(
            name="search_documents",
            description="Search local vector database for matching document chunks.",
            func=search_documents
        ), agent_name=self.name)
        
        self.tools_registry.register(Tool(
            name="answer_question",
            description="Perform a RAG pipeline search and use LLM to answer questions using context.",
            func=answer_question
        ), agent_name=self.name)
        
        self.tools_registry.register(Tool(
            name="get_documents",
            description="Fetch a list of all uploaded documents metadata from the database.",
            func=get_documents
        ), agent_name=self.name)

    def execute(self, request: AgentRequest, context: Optional[AgentContext] = None) -> AgentResponse:
        payload = request.payload or {}
        action = payload.get("action")

        if action == "search_documents":
            query = payload.get("query") or request.message
            result = self.tools_registry.execute_tool("search_documents", query=query)
            return AgentResponse(
                source=self.name,
                response_text="Search completed.",
                data=result if isinstance(result, dict) else {"result": result},
                model=request.model
            )

        elif action == "get_documents":
            docs = self.tools_registry.execute_tool("get_documents")
            return AgentResponse(
                source=self.name,
                response_text="Documents list retrieved.",
                data={"documents": docs},
                model=request.model
            )

        else:
            # Default fallback: answer conversational query using standard RAG tools
            result = self.tools_registry.execute_tool(
                "answer_question",
                question=request.message,
                model=request.model
            )
            raw_response = result.get("response") if isinstance(result, dict) else result
            if isinstance(raw_response, dict):
                response_text = raw_response.get("response") or "I could not find that information in the uploaded documents."
            else:
                response_text = str(raw_response) if raw_response else "I could not find that information in the uploaded documents."

            return AgentResponse(
                source="documents", # Source 'documents' matches the React frontend's badge classification
                response_text=response_text,
                data=result if isinstance(result, dict) else {"result": result},
                model=request.model
            )
