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
        action = payload.get("action") or request.intent or ""
        msg_lower = request.message.lower()

        # Determine action if not explicitly specified in payload
        if not action:
            if "sprint" in msg_lower or "summary" in msg_lower:
                action = "GENERATE_SPRINT_SUMMARY"
            elif "create" in msg_lower or "add task" in msg_lower or "new task" in msg_lower:
                action = "CREATE_TASK"
            elif "update" in msg_lower or "change status" in msg_lower or "move to" in msg_lower or "mark as" in msg_lower:
                action = "UPDATE_TASK_STATUS"
            else:
                action = "SHOW_TASKS"

        if action in ["SHOW_TASKS", "get_tasks"]:
            tasks = self.tools_registry.execute_tool("get_tasks")
            answer = "Your current tasks:\n\n"
            for index, task in enumerate(tasks, start=1):
                answer += f"{index}. {task['name']} ({task['status']})\n"
                
            return AgentResponse(
                source=self.name,
                response_text=answer,
                data={"tasks": tasks},
                model=request.model
            )

        elif action in ["CREATE_TASK", "create_task"]:
            title = payload.get("title") or payload.get("task_name") or request.message
            description = payload.get("description", "")
            task = self.tools_registry.execute_tool("create_task", title=title, description=description)
            
            answer = (
                f"Task created successfully.\n\n"
                f"Task: {task['name']}\n"
                f"Status: {task['status']}"
            )
            return AgentResponse(
                source=self.name,
                response_text=answer,
                data={"task": task},
                model=request.model
            )

        elif action in ["UPDATE_TASK_STATUS", "update_task_status"]:
            task_name = payload.get("task_name") or request.message
            status = payload.get("status") or "complete"
            
            task = self.tools_registry.execute_tool("find_task_by_name", task_name=task_name)
            if not task:
                return AgentResponse(
                    source=self.name,
                    response_text=f"Task '{task_name}' not found.",
                    model=request.model
                )

            updated = self.tools_registry.execute_tool("update_task_status", task_id=task["id"], status=status)
            answer = (
                f"Task updated successfully.\n\n"
                f"Task: {updated['name']}\n"
                f"Status: {updated['status']}"
            )
            return AgentResponse(
                source=self.name,
                response_text=answer,
                data={"task": updated},
                model=request.model
            )

        elif action in ["GENERATE_SPRINT_SUMMARY", "generate_sprint_summary"]:
            summary = self.tools_registry.execute_tool("generate_sprint_summary", model=request.model)
            return AgentResponse(
                source=self.name,
                response_text=summary,
                data={"summary": summary},
                model=request.model
            )

        else:
            # Default action for ClickUp queries
            tasks = self.tools_registry.execute_tool("get_tasks")
            answer = "Your current tasks:\n\n"
            for index, task in enumerate(tasks, start=1):
                answer += f"{index}. {task['name']} ({task['status']})\n"
                
            return AgentResponse(
                source=self.name,
                response_text=answer,
                data={"tasks": tasks},
                model=request.model
            )