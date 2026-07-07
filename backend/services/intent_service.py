import json

from services.ai_manager import AIManager


class IntentService:

    def __init__(self):
        self.ai_manager = AIManager()

    def detect(self, message, model="auto"):

        prompt = f"""
You are an intent classifier.

Return ONLY valid JSON.

Supported intents:

SHOW_TASKS

CREATE_TASK

UPDATE_TASK_STATUS

CHAT

For UPDATE_TASK_STATUS return:

{{
    "intent":"UPDATE_TASK_STATUS",
    "task_name":"",
    "status":""
}}

For CREATE_TASK return:

{{
    "intent":"CREATE_TASK",
    "title":""
}}

For SHOW_TASKS:

{{
    "intent":"SHOW_TASKS"
}}

For GENERATE_SPRINT_SUMMARY return:

{{
    "intent":"GENERATE_SPRINT_SUMMARY"
}}

If none match:

{{
    "intent":"CHAT"
}}

User:

{message}
"""

        response = self.ai_manager.generate(
            prompt=prompt,
            model=model
        )

        text = response["response"]
        
        print("\n========== AI RESPONSE ==========")
        print(response)
        print(type(response))

        text = response.get("response", "")

        print("\n========== TEXT ==========")
        print(repr(text))
        
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

        print("\n========== CLEANED TEXT ==========")
        print(repr(text))

        return json.loads(text)