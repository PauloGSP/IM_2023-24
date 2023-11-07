# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from rasa_sdk import Action, Tracker
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List

import datetime
import os.path

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def write_log(text):
    with open("log.txt", "a") as log:
        log.write(text)

def get_credentials(self) -> Credentials:
    """Gets valid user credentials from storage."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        write_log("Actions: " + "No_understand: " + "enter\n")
        
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))
        write_log("Confiança: " + str(tracker.latest_message["intent"].get("confidence")) + "\n")
        
        if tracker.latest_message["intent"].get("confidence") > 0.5:
            dispatcher.utter_message(response="utter_default")
        
        #publish.single(topic="comandos/voz/UI", payload=json.dumps({"comando": "no_understand"}), hostname="localhost")
        
        write_log("Actions: " + "No_understand: " + "exit\n")
        
        # Revert user message which led to fallback.
        return [UserUtteranceReverted()]
    
class ActionListAllEvents(Action):

    def name(self) -> Text:
        return "action_list_all_events"

    async def run(
        self, 
        dispatcher: CollectingDispatcher, 
        tracker: Tracker, 
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message("Bilhaaaaaaaaaa")

        if tracker.latest_message["intent"].get("confidence") < 0.8:
            dispatcher.utter_message(response="utter_default")

        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            dispatcher.utter_message(text="No upcoming events found.")
        else:
            # Format the events into a response
            message = "Here are your upcoming events:"
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                message += f"\n- {event['summary']} at {start}"
            dispatcher.utter_message(text=message)

        return []

class ActionListAllEventsOfADate(Action):
    
    def name(self) -> Text:
        return "action_list_all_events_of_a_date"
    
    async def run(
            self, 
            dispatcher: CollectingDispatcher, 
            tracker: Tracker, 
            domain: Dict[Text, Any]
        ) -> List[Dict[Text, Any]]:

        if tracker.latest_message["intent"].get("confidence") < 0.8:
            dispatcher.utter_message(response="utter_default")

        day = tracker.get_slot('day')
        month = tracker.get_slot('month')
        year = tracker.get_slot('year')

        events_list = None # TODO FAZER A SAUCE :)

        dispatcher.utter_message(response="utter_confirm_date", day=day, month=month, year=year)
        dispatcher.utter_message(response="utter_events_listed", events=events_list)

class ActionAfirmar(Action):
    
    def name(self) -> Text:
        return "action_afirmar"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        write_log("Actions: " + "Afirmar: " + "enter\n")
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))
        write_log("Confiança: " + str(tracker.latest_message["intent"].get("confidence")) + "\n")
        
        msg = {"comando": "confirmar"}
        # publish.single(topic="comandos/voz/UI", payload=json.dumps(msg), hostname="localhost")
        
        write_log("Actions: " + "Afirmar: " + "exit\n")
        
        return []

class ActionNegar(Action):
    
    def name(self) -> Text:
        return "action_negar"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        write_log("Actions: " + "Negar: " + "enter\n")
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))
        write_log("Confiança: " + str(tracker.latest_message["intent"].get("confidence")) + "\n")
        
        msg = {"comando": "negar"}
        # publish.single(topic="comandos/voz/UI", payload=json.dumps(msg), hostname="localhost")
        
        write_log("Actions: " + "Negar: " + "exit\n")
        
        return []