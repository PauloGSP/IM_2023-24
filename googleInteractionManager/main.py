import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly","https://www.googleapis.com/auth/calendar"]

class CreateEvent(BaseModel):
    day: str
    month: str
    year: str
    event_title: str
    event_time: str
    event_color: str

@app.get("/list_all_events/")
async def list_all_events():

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token: 
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return []

        return events

    except HttpError as error:
        print(f"An error occurred: {error}")


@app.post("/create_new_event/")
async def create_event(event: CreateEvent):
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token: 
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        new_event = {
            'summary': event.event_title,
            'description': '',
            'start': {
                'dateTime': f'{event.year}-{event.month}-{event.day}T{event.event_time}:00Z',
                'timeZone': 'Europe/Lisbon'
            },
            'reminders': {
                'useDefault': True
            }
        }

        event = service.events().insert(calendarId='primary', body=new_event).execute()
        return event
        
    except HttpError as error:
        print(f"An error occurred: {error}")