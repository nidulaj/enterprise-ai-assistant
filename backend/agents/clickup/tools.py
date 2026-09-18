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

def create_task(title=None, name=None, description=""):
    task_title = title or name or "New Task"
    task = _service.create_task(
        name=task_title,
        description=description,
    )
    return {
        "id": task["id"],
        "name": task["name"],
        "status": task["status"]["status"],
    }

def update_task_status(task_name=None, task_id=None, status="complete", title=None):
    # Normalize status string to match ClickUp workspace conventions
    status_str = str(status or "complete").lower().strip()
    if status_str in ["done", "completed", "finish", "finished", "close", "closed"]:
        normalized_status = "complete"
    elif status_str in ["in-progress", "doing", "progress", "started", "active"]:
        normalized_status = "in progress"
    elif status_str in ["todo", "to-do", "open", "backlog", "pending"]:
        normalized_status = "to do"
    else:
        normalized_status = status_str

    target_name = task_name or title
    if not task_id and target_name:
        task = find_task_by_name(target_name)
        if not task:
            return {"error": f"Task '{target_name}' not found in ClickUp workspace."}
        task_id = task["id"]

    if not task_id:
        return {"error": "Neither task_id nor task_name was provided to update status."}

    task = _service.update_task(
        task_id=task_id,
        status=normalized_status,
    )
    return {
        "id": task["id"],
        "name": task["name"],
        "status": task["status"]["status"],
    }

def find_task_by_name(task_name):
    if not task_name:
        return None

    tasks = get_tasks()
    if not tasks:
        return None

    clean_target = str(task_name).strip().lower()

    # 1. Exact case-insensitive match
    for task in tasks:
        if task["name"].strip().lower() == clean_target:
            return task

    # 2. Substring match (e.g. task name inside user phrase or vice versa)
    for task in tasks:
        t_name = task["name"].strip().lower()
        if t_name and (t_name in clean_target or clean_target in t_name):
            return task

    # 3. Fuzzy search match
    names = [task["name"] for task in tasks]
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