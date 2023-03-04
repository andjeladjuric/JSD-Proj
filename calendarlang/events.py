from datetime import datetime, time, timedelta
import pytz,json

class Events():
    def create_event(self, calendar_service, calendar_model):
        for event in calendar_model.events:
            start_time = datetime(2023, 3, 10, 8, 0, tzinfo= pytz.timezone(event.time.eventTimeZone))
            end_time = start_time + timedelta(hours=1)

            emails=[]
            for guest in event.guests:
                emails.append( {'email': guest})

            recurrence='RRULE:'
            if (event.recurrence.freq != None):
                recurrence+='FREQ='+event.recurrence.freq+';'
             
            if (event.recurrence.count != None):
                recurrence+='COUNT='+str(event.recurrence.count)+';'
             
            if (event.recurrence.interval != None):
                recurrence+='INTERVAL='+str(event.recurrence.interval)+';'
             
            if (event.recurrence.byMonth != []):
                byMonth = ''
                for month in event.recurrence.byMonth:
                    byMonth += str(month) + ","
                recurrence+='BYMONTH='+byMonth+';'

            if (event.recurrence.byMonthDay != []):
                byMonthDay = ''
                for monthDay in event.recurrence.byMonthDay:
                    byMonthDay += str(monthDay) + ","
                recurrence += 'BYMONTHDAY='+byMonthDay+';'
            elif (event.recurrence.byDay != []) :
                byDay = ''
                for day in event.recurrence.byDay:
                    byDay += str(day) + ","
                recurrence += 'BYDAY='+byDay+';'
            
            event_data = {
            'summary': event.title,
            'location': event.time.eventLocation,
            'description': event.description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone':  event.time.eventTimeZone,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone':  event.time.eventTimeZone,
            },
            'recurrence': [
                recurrence
            ],
            'attendees': emails
            ,
            'reminders': {
                'useDefault': True,
            },
            'visibility': event.visibility,
            'guestsCanSeeOtherGuests': True,
            'guestsCanInviteOthers': True
            }

            calendar_service.events().insert(calendarId="primary", body=event_data).execute()

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