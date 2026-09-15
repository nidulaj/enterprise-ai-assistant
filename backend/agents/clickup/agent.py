from typing import Optional
from agents.base.agent import BaseAgent
from agents.base.models import AgentRequest, AgentResponse
from agents.base.context import AgentContext
from agents.base.tool import Tool
from agents.clickup.tools import (
    get_tasks,
    create_task,
    get_task,
    update_task_status,
    find_task_by_name,
    generate_sprint_summary,
)

class ClickUpAgent(BaseAgent):
    name = "clickup"
    description = "Handles ClickUp tasks, sprints, task creation, status updates, and project management summaries."
    capabilities = [
        "View workspace tasks and status",
        "Create new project tasks with titles and descriptions",
        "Update task status (e.g. to complete, in progress)",
        "Search tasks by fuzzy name matching",
        "Generate automated sprint summaries"
    ]

    def register_tools(self) -> None:
        self.tools_registry.register(Tool(
            name="get_tasks",
            description="Retrieve list of all tasks from the ClickUp workspace.",
            func=get_tasks
        ), agent_name=self.name)
        
        self.tools_registry.register(Tool(
            name="create_task",
            description="Create a new task with a title and optional description.",
            func=create_task
        ), agent_name=self.name)
        
        self.tools_registry.register(Tool(
            name="get_task",
            description="Get details of a specific task by its unique ID.",
            func=get_task
        ), agent_name=self.name)
        
        self.tools_registry.register(Tool(
            name="update_task_status",
            description="Update the state/status of an existing task.",
            func=update_task_status
        ), agent_name=self.name)
        
        self.tools_registry.register(Tool(
            name="find_task_by_name",
            description="Perform a fuzzy search to find a task matching a name query.",
            func=find_task_by_name
        ), agent_name=self.name)
        
        self.tools_registry.register(Tool(
            name="generate_sprint_summary",
            description="Synthesize a professional summary of the current sprint tasks.",
            func=generate_sprint_summary
        ), agent_name=self.name)

    def execute(self, request: AgentRequest, context: Optional[AgentContext] = None) -> AgentResponse:
        payload = request.payload or {}
        action = payload.get("action")
        msg_lower = request.message.lower()

        # 1. Dynamically resolve tool from action or message hint
        tool = self.resolve_tool(action_name=action, message_hint=request.message)

        # 2. Fallback heuristic if resolution was ambiguous
        if not tool:
            if any(k in msg_lower for k in ["create", "add task", "new task"]):
                tool = self.tools_registry.get("create_task")
            elif any(k in msg_lower for k in ["update", "status", "change status", "move to", "mark as"]):
                tool = self.tools_registry.get("update_task_status")
            elif any(k in msg_lower for k in ["summary", "sprint summary", "summarize"]):
                tool = self.tools_registry.get("generate_sprint_summary")
            else:
                tool = self.tools_registry.get("get_tasks")

        tool_name = tool.name if tool else "get_tasks"

        # 3. Dynamic execution with formatted response contracts
        if tool_name == "create_task":
            # Extract title flexibly
            title = payload.get("title") or payload.get("task_name") or payload.get("name") or payload.get("task")
            if not title:
                # Clean prefix from message if title wasn't extracted
                cleaned_msg = request.message.strip()
                for prefix in [
                    "create a task called ", "create task called ", "create a new task called ",
                    "create new task called ", "add a task called ", "add task called ",
                    "create a task ", "create task ", "create new task ", "add a task ", "add task "
                ]:
                    if cleaned_msg.lower().startswith(prefix):
                        cleaned_msg = cleaned_msg[len(prefix):].strip(" '\"")
                        break
                title = cleaned_msg or "New Task"

            description = payload.get("description", "")
            task = self.execute_dynamic_tool("create_task", {"title": title, "description": description})
            
            answer = (
                f"Task created successfully.\n\n"
                f"Task: {task.get('name')}\n"
                f"Status: {task.get('status')}"
            )
            return AgentResponse(
                source=self.name,
                response_text=answer,
                data={"task": task},
                model=request.model
            )

        elif tool_name == "update_task_status":
            task_name = payload.get("task_name") or payload.get("title") or payload.get("task") or payload.get("name") or request.message
            status = payload.get("status") or payload.get("new_status") or "complete"
            
            result = self.execute_dynamic_tool("update_task_status", {
                "task_name": task_name,
                "status": status
            })

            if isinstance(result, dict) and "error" in result:
                return AgentResponse(
                    source=self.name,
                    response_text=result["error"],
                    data=result,
                    model=request.model
                )

            answer = (
                f"Task updated successfully.\n\n"
                f"Task: {result.get('name')}\n"
                f"Status: {result.get('status')}"
            )
            return AgentResponse(
                source=self.name,
                response_text=answer,
                data={"task": result},
                model=request.model
            )

        elif tool_name == "generate_sprint_summary":
            summary = self.execute_dynamic_tool("generate_sprint_summary", {"model": request.model})
            return AgentResponse(
                source=self.name,
                response_text=summary,
                data={"summary": summary},
                model=request.model
            )

        elif tool_name == "get_tasks":
            tasks = self.execute_dynamic_tool("get_tasks")
            answer = "Your current tasks:\n\n"
            for index, task in enumerate(tasks, start=1):
                answer += f"{index}. {task['name']} ({task['status']})\n"
                
            return AgentResponse(
                source=self.name,
                response_text=answer,
                data={"tasks": tasks},
                model=request.model
            )

        else:
            # Fallback for any other dynamically registered tool
            result = self.execute_dynamic_tool(tool_name, payload)
            return AgentResponse(
                source=self.name,
                response_text=str(result),
                data={"result": result} if isinstance(result, dict) else {"data": result},
                model=request.model
            )