import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ClickUpService:
    BASE_URL = "https://api.clickup.com/api/v2"
    
    def __init__(self):
        self.api_key = os.getenv("CLICKUP_API_KEY")
        self.list_id = os.getenv("CLICKUP_LIST_ID")
        
        if not self.api_key:
            raise ValueError("CLICKUP_API_KEY is missing.")
        
        if not self.list_id:
            raise ValueError("CLICKUP_LIST_ID is missing.")
        
        self.headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        
    def get_tasks(self):
        url = f"{self.BASE_URL}/list/{self.list_id}/task"
        
        params = {
        "include_closed": "true"
        }
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_task(self, task_id):
        url = f"{self.BASE_URL}/task/{task_id}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def create_task(self, name, description=""):
        
        url =  f"{self.BASE_URL}/list/{self.list_id}/task"
        payload = {
            "name": name,
            "description": description
        }
        
        response = requests.post(
            url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def update_task(self, task_id, status):
        
        url = f"{self.BASE_URL}/task/{task_id}"
        payload={
            "status": status
        }
        
        print("\n========== CLICKUP UPDATE ==========")
        print("URL:", url)
        print("PAYLOAD:", payload)
        
        response = requests.put(
            url,
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()