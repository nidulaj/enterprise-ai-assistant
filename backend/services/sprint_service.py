from clickup.clickup_service import ClickUpService
from services.ai_manager import AIManager


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

        prompt = f"""
You are an Agile Scrum assistant.

Below are the current sprint tasks.

Tasks:

{task_text}

Generate a professional sprint summary.

Requirements:

1. Group tasks into:

Completed

In Progress

Pending

2. Count the tasks.

3. Mention overall sprint progress.

4. Mention risks if there are many pending tasks.

5. Keep the response concise.

Use markdown.
"""

        response = self.ai.generate(
            prompt=prompt,
            model=model
        )

        return response["response"]