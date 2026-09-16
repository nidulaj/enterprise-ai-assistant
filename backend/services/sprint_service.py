from services.clickup_service import ClickUpService
from services.llm.ai_manager import AIManager


class SprintService:

    def __init__(self):
        self.clickup = ClickUpService()
        self.ai = AIManager()

    def generate_summary(self, model="auto"):

        raw_tasks = self.clickup.get_tasks()
        
        # ClickUp API returns {"tasks": [...]}, extract the task list
        if isinstance(raw_tasks, dict):
            tasks = raw_tasks.get("tasks", [])
        elif isinstance(raw_tasks, list):
            tasks = raw_tasks
        else:
            tasks = []

        if not tasks:
            return "No tasks found in the current sprint."

        task_text = ""

        for task in tasks:
            if isinstance(task, dict):
                name = task.get("name", "Unnamed Task")
                status_raw = task.get("status")
                if isinstance(status_raw, dict):
                    status = status_raw.get("status", "unknown")
                else:
                    status = str(status_raw or "unknown")

                task_text += (
                    f"- {name} "
                    f"(Status: {status})\n"
                )

        from agents.clickup.prompts import SPRINT_SUMMARY_PROMPT
        prompt = SPRINT_SUMMARY_PROMPT.format(task_text=task_text)

        response = self.ai.generate(
            prompt=prompt,
            model=model
        )

        if isinstance(response, dict):
            return response.get("response", str(response))
        return str(response)