from clickup_client import ClickUpClient

client = ClickUpClient()
tasks = client.get_tasks()
print(tasks)