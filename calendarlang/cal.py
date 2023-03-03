from textx import metamodel_from_file
from os.path import dirname, join

import google.auth
from google.oauth2 import service_account
import googleapiclient.discovery

def connect_with_google_calendar():
    service_account_file = 'config.json'
    # scopes required to access the Google Calendar API
    scopes = ['https://www.googleapis.com/auth/calendar']

    # authenticate with the service account
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scopes)
    
    calendar_service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    # list all events in given calendar
    events_result = calendar_service.events().list(calendarId='jsdmaster2023@gmail.com').execute()
    events = events_result.get('items', [])
    print(events)

def main(file_name):
    this_folder = dirname(__file__)
    calendar_mm = metamodel_from_file(join(this_folder, 'calendarlang.tx'), debug=False)
    calendar_model = calendar_mm.model_from_file(file_name)
    
    print(calendar_model.owner.email) #checking if the model is valid
    connect_with_google_calendar();

if __name__ == "__main__":
    main("calendarExample.cal")
