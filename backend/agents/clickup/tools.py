from rapidfuzz import process
from services.clickup_service import ClickUpService

_service = ClickUpService()

def get_tasks():
    response = _service.get_tasks()
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

def get_task(task_id):
    task = _service.get_task(task_id)
    return {
        "id": task["id"],
        "name": task["name"],
        "status": task["status"]["status"],
    }

def create_task(title, description=""):
    task = _service.create_task(
        name=title,
        description=description,
    )
    return {
        "id": task["id"],
        "name": task["name"],
        "status": task["status"]["status"],
    }

def update_task_status(task_id, status):
    task = _service.update_task(
        task_id=task_id,
        status=status,
    )
    return {
        "id": task["id"],
        "name": task["name"],
        "status": task["status"]["status"],
    }

def find_task_by_name(task_name):
    tasks = get_tasks()
    
    if not tasks:
        return None
    
    names = [
        task["name"]
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
        if task["name"] == matched_name:
            return task

    return None

def generate_sprint_summary(model="auto"):
    """
    Generate a formatted sprint summary based on clickup tasks.
    """
    from services.sprint_service import SprintService
    sprint_service = SprintService()
    return sprint_service.generate_summary(model=model)