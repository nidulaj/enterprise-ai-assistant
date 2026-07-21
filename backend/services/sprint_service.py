from services.clickup_service import ClickUpService
from services.llm.ai_manager import AIManager


class SprintService:

    def __init__(self):
        self.clickup = ClickUpService()
        self.ai = AIManager()

    def generate_summary(self, model="auto"):

        tasks = self.clickup.get_tasks()

        if not tasks:
            return "No tasks found."

        task_text = ""

        for task in tasks:

            task_text += (
                f"- {task['name']} "
                f"(Status: {task['status']})\n"
            )

        from agents.clickup.prompts import SPRINT_SUMMARY_PROMPT
        prompt = SPRINT_SUMMARY_PROMPT.format(task_text=task_text)

        response = self.ai.generate(
            prompt=prompt,
            model=model
        )

        return response["response"]