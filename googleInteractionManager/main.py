import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly","https://www.googleapis.com/auth/calendar"]

class CreateEvent(BaseModel):
    day: str
    month: str
    year: str
    event_title: str
    event_time: str
    event_color: str
    event_description: str

class Date(BaseModel):
    day: str
    month: str
    year: str 

class Cor(BaseModel):
    cor: str

class Title(BaseModel):
    title: str

def getCredentials():
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

    return creds


@app.get("/list_all_events/")
async def list_all_events():

    creds = getCredentials()

    try:
        service = build("calendar", "v3", credentials=creds)


        events_result = (
            service.events()
            .list(
                calendarId="primary",
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

@app.post("/list_all_events_of_a_date/")
async def list_all_events_of_a_date(date: Date):

    creds = getCredentials()

    try:
        service = build("calendar", "v3", credentials=creds)
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No events found.")
            return []

        event_of_date = []

        dateIsoFormat = f"{date.year}-{date.month}-{date.day}"

        for e in events:
            print(e["start"])
            try:
                if dateIsoFormat in e["start"]["dateTime"]:
                    event_of_date.append(e)
            except:
                if dateIsoFormat in e["start"]["date"]:
                    event_of_date.append(e)

        return event_of_date

    except HttpError as error:
        print(f"An error occurred: {error}")

@app.post("/list_all_events_of_a_color_tag/")
async def list_all_events_of_a_color_tag(cor: Cor):

    creds = getCredentials()

    try:
        service = build("calendar", "v3", credentials=creds)
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No events found.")
            return []

        event_of_a_color_tag = []

        color_path = {
            "tomate": 11,
            "tangerina": 6,
            "salva": 2,
            "pavão": None,
            "lavanda": 1,
            "grafite": 8,
            "flamingo": 4,
            "banana": 5,
            "manjericão": 10,
            "mirtilo": 9,
            "uva": 3,
        }

        for e in events:
            if "colorId" in e.keys():
                if str(color_path[cor.cor]) == str(e["colorId"]):
                    event_of_a_color_tag.append(e)
            elif cor.cor == "pavão":
                event_of_a_color_tag.append(e)

        return event_of_a_color_tag

    except HttpError as error:
        print(f"An error occurred: {error}")

@app.post("/list_an_event_by_title/")
async def list_an_event_by_title(title: Title):

    creds = getCredentials()

    try:
        service = build("calendar", "v3", credentials=creds)
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No events found.")
            return []

        event_by_title = []

        for e in events:
            if title.title.lower() in e["summary"].lower():
                event_by_title.append(e)
        return event_by_title

    except HttpError as error:
        print(f"An error occurred: {error}")

@app.post("/create_new_event/")
async def create_event(event: CreateEvent):
    
    creds = getCredentials()

    try:
        service = build("calendar", "v3", credentials=creds)

        new_event = {
            'summary': event.event_title,
            'description': event.event_description,
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