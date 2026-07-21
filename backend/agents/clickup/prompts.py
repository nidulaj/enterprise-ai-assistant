SPRINT_SUMMARY_PROMPT = """You are an Agile Scrum assistant.

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
