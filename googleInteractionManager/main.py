from datetime import datetime, timedelta
import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from fastapi import FastAPI
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

def detectDay(inputStr : str):

    inputStrSplit = inputStr.lower().split(" ")

    number_mapping = {
        'um': "1", 'uma': "1",'dois': "2", 'duas': "2", 'três': "3", 'quatro': "4",
        'cinco': "5", 'seis': "6", 'sete': "7", 'oito': "8", 'nove': "9",
        'dez': "10", 'onze': "11", 'doze': "12", 'treze': "13", 'quatorze': "14",
        'quinze': "15", 'dezesseis': "16", 'dezessete': "17", 'dezoito': "18", 'dezenove': "19",
        'vinte': "20", 'trinta': "30", 'quarenta': "40", 'cinquenta': "50",
        'sessenta': "60", 'setenta': "70", 'oitenta': "80", 'noventa': "90",
        'cem': "100", 'duzentos': "200", 'trezentos': "300", 'quatrocentos': "400",
        'quinhentos': "500", 'seiscentos': "600", 'setecentos': "700", 'oitocentos': "800",
        'novecentos': "900", 'mil': "1000"
    }

    if "hoje" in inputStrSplit:
        return ["current",0,0,0,0]
    if "amanhã" in inputStrSplit:
        return ["current",1,0,0,0]
    if "ontem" in inputStrSplit:
        return ["current",-1,0,0,0]
    if "anteontem" in inputStrSplit:
        return ["current",-2,0,0,0]


    for i, term in enumerate(inputStrSplit):
        
        value = None
        if "est" in term:
           value = "current"

        if "daqui" in term:
            value = "fromto"

        if "próxim" in term :
            value = "next"

        if value != None:
            try:
                number = 1
                for new_term in inputStrSplit[i+1:]:
                    if new_term in number_mapping.keys():
                        number += int(number_mapping[new_term])
                    if new_term in number_mapping.values():
                        number += int(new_term)
                    if new_term == "dia" or new_term == "dias":
                        if number==1: number=2
                        return [value,number-1,0,0,0]
                    if new_term == "semana" or new_term == "semanas":
                        if number==1: number=2
                        return [value,0,number-1,0,0]
                    if new_term == "mês" or new_term == "meses":
                        if number==1: number=2
                        return [value,0,0,number-1,0]
                    if new_term == "ano" or new_term == "anos":
                        if number==1: number=2
                        return [value,0,0,0,number-1]
            except: pass

    return None, None, None, None, None

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
                timeMin=datetime.utcnow().isoformat() + "Z", # 'Z' indicates UTC time
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

@app.post("/list_all_events_of_a_day/")
async def list_all_events_of_a_day(date: dict):

    creds = getCredentials()

    alphaMonths = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    values = []

    if "day" in date.keys():
        for v in re.split('[^a-zA-Z0-9]', date["day"]):
            values.append(v)

    if "month" in date.keys():
        for v in re.split('[^a-zA-Z0-9]', date["month"]):
            values.append(v)

    if "year" in date.keys():
        for v in re.split('[^a-zA-Z0-9]', date["year"]):
            values.append(v)

    for v in values:
        if not v.isnumeric() and v not in alphaMonths:
            values.remove(v)

    dateIsoFormat = None
    if len(values)==3:
        if not values[1].isnumeric():
            values[1] = alphaMonths.index(values[1])+1
        dateIsoFormat = f"{values[2]}-{values[1]}-{values[0]}"
        print(dateIsoFormat)

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

@app.post("/list_all_events_of_a_date/")
async def list_all_events_of_a_date(date: dict):

    code, days, weeks, months, years = detectDay(date["date"])
    print(code, days, weeks, months, years)

    creds = getCredentials()
    
    start_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)

    if code == "current":
        if days != 0:
            start_date = start_date + timedelta(days=days)
            end_date = start_date + timedelta(days=1)
        elif weeks != 0:
            start_date = start_date - timedelta(days=start_date.weekday())
            end_date = start_date + timedelta(weeks=1)
        elif months != 0:
            start_date = start_date.replace(day=1)
            end_date = (start_date + timedelta(days=32)).replace(day=1)
        elif years != 0:
            start_date = start_date.replace(day=1, month=1)
            end_date = (start_date + timedelta(days=366)).replace(day=1, month=1)

    if code == "fromto":
        if days != 0:
            start_date = start_date + timedelta(days=days)
            end_date = start_date + timedelta(days=1)
        elif weeks != 0:
            start_date = start_date + timedelta(weeks=weeks)
            end_date = start_date + timedelta(days=1)
        elif months != 0:
            start_date = (start_date.replace(day=1) + timedelta(days=32*months)).replace(day=start_date.day)
            end_date = start_date + timedelta(days=1)
        elif years != 0:
            start_date = (start_date.replace(day=1, month=1) + timedelta(days=365*years)).replace(day=start_date.day)
            end_date = start_date + timedelta(days=1)

    if code == "next":
        if days != 0:
            end_date = start_date + timedelta(days=days)
        elif weeks != 0:
            start_date = start_date - timedelta(days=start_date.weekday()) + timedelta(weeks=1)
            end_date = start_date + timedelta(weeks=weeks)
        elif months != 0:
            start_date = (start_date.replace(day=1) + timedelta(days=32)).replace(day=1)
            end_date = (start_date + timedelta(days=32)).replace(day=1)
        elif years != 0:
            start_date = (start_date.replace(day=1, month=1) + timedelta(days=366)).replace(day=1)
            end_date = (start_date + timedelta(days=366*years)).replace(day=1)

    start_date = start_date.isoformat() + "Z"
    end_date = end_date.isoformat() + "Z"
    print(start_date)
    print(end_date)

    try:
        service = build("calendar", "v3", credentials=creds)

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_date,
                timeMax=end_date,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return []

        ev = []
        for e in events:
            ev.append(e["summary"])
            print(e["summary"])
        return ev

    except HttpError as error:
        print(f"An error occurred: {error}")

@app.post("/list_all_events_of_a_color_tag/")
async def list_all_events_of_a_color_tag(cor: dict):

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
            "tomate": "11",
            "tangerina": "6",
            "salva": "2",
            "lavanda": "1",
            "grafite": "8",
            "flamingo": "4",
            "banana": "5",
            "manjericão": "10",
            "mirtilo": "9",
            "uva": "3",
            "pavão": None
        }

        for e in events:
            if "colorId" in e.keys() and cor["cor"] in color_path.keys():
                if color_path[cor["cor"]] == str(e["colorId"]):
                    event_of_a_color_tag.append(e)
            elif cor["cor"] == "pavão":
                event_of_a_color_tag.append(e)

        return event_of_a_color_tag

    except HttpError as error:
        print(f"An error occurred: {error}")

@app.post("/list_an_event_by_title/")
async def list_an_event_by_title(title: dict):

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
            if title["title"].lower() in e["summary"].lower():
                event_by_title.append(e)
        return event_by_title

    except HttpError as error:
        print(f"An error occurred: {error}")

@app.post("/create_new_event/")
async def create_event(event: dict):
    
    creds = getCredentials()

    try:
        service = build("calendar", "v3", credentials=creds)

        new_event = {
            'summary': event["title"],
            'description': event["event_description"],
            'start': {
                'dateTime': f'{event["year"]}-{event["month"]}-{event["day"]}T{event["time"]}:00Z',
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

@app.post("/provide_event_day/")
async def provide_day(date: dict):
    alphaMonths = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    values = []

    if "day" in date.keys():
        for v in re.split('[^a-zA-Z0-9]', date["day"]):
            values.append(v)

    if "month" in date.keys():
        for v in re.split('[^a-zA-Z0-9]', date["month"]):
            values.append(v)

    if "year" in date.keys():
        for v in re.split('[^a-zA-Z0-9]', date["year"]):
            values.append(v)

    for v in values:
        if not v.isnumeric() and v not in alphaMonths:
            values.remove(v)

    dateIsoFormat = None
    if len(values)==3:
        if not values[1].isnumeric():
            values[1] = alphaMonths.index(values[1])+1
        dateIsoFormat = f"{values[2]}-{values[1]}-{values[0]}"
        print(dateIsoFormat)

@app.post("/provide_event_date/")
async def provide_date(date: dict):

    _, days, weeks, months, years = detectDay(date["date"])

    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    result_day = today + timedelta(days=days, weeks=weeks)
    for _ in range(months):
        result_day = (result_day + timedelta(days=32)).replace(day=result_day.day)
    for _ in range(years):
        result_day = (result_day + timedelta(days=365)).replace(day=result_day.day, month=result_day.month)

    return result_day