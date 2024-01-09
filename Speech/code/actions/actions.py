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

from rasa_sdk import Action, Tracker
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List

def write_log(text):
    with open("log.txt", "a") as log:
        log.write(text)

class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        write_log("Actions: " + "No_understand: " + "enter\n")
        
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))
        write_log("Confiança: " + str(tracker.latest_message["intent"].get("confidence")) + "\n")
        
        if tracker.latest_message["intent"].get("confidence") > 0.5:
            dispatcher.utter_message(response="utter_default")
        
        write_log("Actions: " + "No_understand: " + "exit\n")
        
        return [UserUtteranceReverted()]
    

class ActionAfirmar(Action):
    
    def name(self) -> Text:
        return "action_afirmar"
    
    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        write_log("Actions: " + "Afirmar: " + "enter\n")
        print("Confiança: ", tracker.latest_message["intent"].get("confidence"))
        write_log("Confiança: " + str(tracker.latest_message["intent"].get("confidence")) + "\n")
        
        
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
        
        write_log("Actions: " + "Negar: " + "exit\n")
        
        return []