from datetime import datetime
import pytz

class Events():
    def check_if_timezone_is_valid(self, calendar_model):
        timezones = set(pytz.all_timezones)

        for event in calendar_model.events:
            if(not event.time.eventTimeZone in timezones):
                return False
            
        return True

    def query_events_by_rule(self, calendar_model, calendar_service):
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