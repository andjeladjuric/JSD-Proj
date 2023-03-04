from textx import metamodel_from_file
from os.path import dirname, join, exists
import pytz
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


def connect_with_google_calendar():
    config_file = 'config.json'
    # scopes required to access the Google Calendar API and Google Tasks API
    scopes = ['https://www.googleapis.com/auth/tasks', 'https://www.googleapis.com/auth/calendar']

    if exists('token.json'):
        credentials = Credentials.from_authorized_user_file('token.json', scopes)
    # if there are no credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config_file, scopes)
            credentials = flow.run_local_server(port=0)
        # save the credentials
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())
    
    calendar_service = build('calendar', 'v3', credentials=credentials)
    tasks_service = build('tasks', 'v1', credentials=credentials)

    return calendar_service, tasks_service

def list_all_events_and_tasks(calendar_service, tasks_service):
     # list all events in given calendar
    events_result = calendar_service.events().list(calendarId='jsdmaster2023@gmail.com').execute()
    events = events_result.get('items', [])
    for event in events:
       print(f'\n{event["summary"]}' +
            f'\n\tstart time: {event["start"]}' +
            f'\n\tend time: {event["end"]}' +
            f'\n\tcreator: {event["creator"]["email"]}' + 
            f'\n\treminders: {event["reminders"]}'
        )
    
    # list all tasks and reminders
    tasks_result = tasks_service.tasks().list(tasklist='@default').execute()
    tasks = tasks_result.get('items', [])
    for task in tasks:
        print(f'\n{task["title"]}' +
            f'\n\tstatus: {task["status"]}' +
            f'\n\tdue: {task["due"]}'
        )

def check_if_timezone_is_valid(calendar_model):
    timezones = set(pytz.all_timezones)

    for event in calendar_model.events:
        if(not event.time.eventTimeZone in timezones):
            return False
        
    return True

def query_events_by_rule(calendar_model, calendar_service):
    found_events = []
    owner = ''

    for rule in calendar_model.findEvents:
        owner = rule.owner
        start_string = f'{rule.start.year}-{rule.start.month}-{rule.start.day}';
        end_string = f'{rule.end.year}-{rule.end.month}-{rule.end.day}';
        start_date = datetime.strptime(start_string, "%Y-%m-%d")
        end_date = datetime.strptime(end_string, "%Y-%m-%d")

        events_result = calendar_service.events().list(
            calendarId='primary',
            timeMin=start_date.isoformat() + 'Z',
            timeMax=end_date.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        found_events.extend(events)

    for event in found_events:
        if(event["creator"].get("email", '') == owner):
            print(f'\n{event["summary"]}' +
                f'\n\tstart time: {event["start"]}' +
                f'\n\tend time: {event["end"]}' +
                f'\n\tcreator: {event["creator"]["email"]}' + 
                f'\n\treminders: {event["reminders"]}'
            )

def main(file_name):
    this_folder = dirname(__file__)
    calendar_mm = metamodel_from_file(join(this_folder, 'calendarlang.tx'), debug=False)
    calendar_model = calendar_mm.model_from_file(file_name)
    
    #checking if the model is valid
    check_if_timezone_is_valid(calendar_model);
    print(calendar_model.owner.email)

    calendar_service, tasks_service = connect_with_google_calendar()
    #list_all_events_and_tasks(calendar_service, tasks_service); #connect with calendar and list all events and tasks
    query_events_by_rule(calendar_model, calendar_service)

if __name__ == "__main__":
    main("calendarExample.cal")
