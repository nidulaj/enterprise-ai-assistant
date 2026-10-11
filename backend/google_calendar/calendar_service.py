import datetime
import os
import os.path
import uuid

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
        request_id = uuid.uuid4().hex
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
                    "requestId": request_id,
                    "conferenceSolutionKey": {"type": "hangoutsMeet"}
                }
            }
        }
        
        try:
            created_event = self.service.events().insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1
            ).execute()
        except Exception as e:
            # If conference creation failed (e.g. conferenceData error), fallback without conference
            err_str = str(e).lower()
            if "conferencedata" in err_str or "conferencesolutionkey" in err_str or "badrequest" in err_str:
                event_no_conf = {
                    "summary": summary,
                    "start": {
                        "dateTime": start_time,
                        "timeZone": "Asia/Colombo",
                    },
                    "end": {
                        "dateTime": end_time,
                        "timeZone": "Asia/Colombo",
                    }
                }
                created_event = self.service.events().insert(
                    calendarId="primary",
                    body=event_no_conf
                ).execute()
            else:
                raise e
        
        meet_link = None
        conference = created_event.get("conferenceData")
        
        if conference:
            for entry in conference.get("entryPoints", []):
                if entry.get("entryPointType") == "video":
                    meet_link = entry.get("uri")
                    break
            
        return {
            "summary": created_event.get("summary", summary),
            "start_time": created_event.get("start", {}).get("dateTime", start_time),
            "end_time": created_event.get("end", {}).get("dateTime", end_time),
            "meet_link": meet_link
        }