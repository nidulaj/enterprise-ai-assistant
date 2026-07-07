from rapidfuzz import process

from clickup.clickup_client import ClickUpClient

class ClickUpService:

    def __init__(self):
        self.client = ClickUpClient()

    def get_tasks(self):
        response = self.client.get_tasks()
        tasks = response.get("tasks", [])

        formatted_tasks = []

        for task in tasks:
            formatted_tasks.append(
                {
                    "id": task["id"],
                    "name": task["name"],
                    "status": task["status"]["status"],
                }
            )

        return formatted_tasks

    def get_task(self, task_id):
        task = self.client.get_task(task_id)

        return {
            "id": task["id"],
            "name": task["name"],
            "status": task["status"]["status"],
        }

    def create_task(self, title, description=""):
        task = self.client.create_task(
            name=title,
            description=description,
        )

        return {
            "id": task["id"],
            "name": task["name"],
            "status": task["status"]["status"],
        }

    def update_task_status(self, task_id, status):
        task = self.client.update_task(
            task_id=task_id,
            status=status,
        )

        return {
            "id": task["id"],
            "name": task["name"],
            "status": task["status"]["status"],
        }

    def find_task_by_name(self, task_name):
        tasks = self.get_tasks()
        
        if not tasks:
            return None
        
        names = [
            tasks["name"]
            for task in tasks
        ]
        
        match = process.extractOne(
            task_name,
            names,
            score_cutoff=60
        )
        if not match:
            return None
        
        matched_name = match[0]

        for task in tasks:
            if task["name"].lower() == task_name.lower():
                return task

        return None