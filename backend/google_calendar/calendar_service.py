import datetime
import os
import os.path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]

class CalendarService:
    def __init__(self):
        self.service = self.authenticate()
        
    def authenticate(self):
        creds = None

        if os.path.exists("token.json"):
            try:
                creds = Credentials.from_authorized_user_file(
                    "token.json",
                    SCOPES
                )
            except Exception:
                creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except (RefreshError, Exception) as e:
                    print(f"Token refresh failed ({e}). Removing invalid token.json...")
                    creds = None
                    if os.path.exists("token.json"):
                        try:
                            os.remove("token.json")
                        except OSError:
                            pass

            if not creds:
                if not os.path.exists("credentials.json"):
                    raise FileNotFoundError("credentials.json file not found for Google Calendar authentication.")
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json",
                    SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)
    
    def create_meeting(self, summary, start_time, end_time):
        
        event = {
            "summary": summary,
            "start": {
                "dateTime": start_time,
                "timeZone": "Asia/Colombo",
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "Asia/Colombo",
            },
            "conferenceData": {
                "createRequest": {
                    "requestId": str(datetime.datetime.now().timestamp()),
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            }
        }
        
        event = self.service.events().insert(
            calendarId="primary",
            body=event,
            conferenceDataVersion=1
        ).execute()
        
        meet_link = None
        conference = event.get("conferenceData")
        
        if conference:
            for entry in conference.get("entryPoints",[]):
                if entry.get("entryPointType") == "video":
                    meet_link = entry.get("uri")
                    break
            
        return{
            "summary": event["summary"],
            "start_time": event["start"]["dateTime"],
            "end_time": event["end"]["dateTime"],
            "meet_link": meet_link
        }