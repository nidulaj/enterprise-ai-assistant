import datetime
import os.path

from google.auth.tranport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES =[
    "https://www.googleapis.com/auth/calendar"
]

class CalenderService:
    def __init__(self):
        self.service = self.authenticate()
        
    def authenticate(self):
        creds = None
        
        if os.path.exist("credentials.json"):
            creds = Credentials.from_authorized_user_file(
                "credentials.json",
                SCOPES
            )
            
        if not creds or not creds.valid:
            creds.refresh(
                request()
            )
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES
            )
            
            creds = flow.run_local_server(
                port=0
            )
            
        with open(
            "token.json",
            "W"
        ) as token:
            token.write(
                creds.to_json()
            )
            
    return build(
        "calender",
        "v3",
        credentials=creds
    )
    
    def create_meeting(selff, title, start_time, end_time):
        
        event = {
            "summary": title,
            "start": {
                "dateTime": start_time,
                "timeZone": "Asia/Colombo"
            },
            "conferenceData":{
                "createRequest":{
                    "requestId": title.replace(
                        " ", "_"
                    )
                }
            }
        }
        
        event = self.service.events().insert(
            calenderId="primary",
            body=event,
            conferenceDataVersion=1
        ).execute()
        
        meet_link = None
        
        if "conferenceData" in event:
            meet_link = event[
                "conferenceData"
            ][
                "entryPoints"
            ][0][
                "uri"
            ]
            
        return{
            "title": event["summary"],
            "start_time": event["start"]["dateTime"],
            "end_time": event["end"]["dateTime"],
            "meet_link" meet_link
        }