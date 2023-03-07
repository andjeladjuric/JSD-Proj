from datetime import datetime
import pytz,json
from requests import HTTPError

class Events():
    def setDefaultForReminders(self,event):
        if (event.notifications != []):
            return False
        return True
    
    def create_reminders(self,event):
        if (event.notifications != []):
            reminders='['
            counter=0

            for reminder in event.notifications:
                counter+=1
                reminders+='{\'method\':\''+ reminder.method + "\',"
                reminders+='\'minutes\':'+ str(reminder.minutes)

                if (counter < len(event.notifications)):
                    reminders+="},"
                else:
                    reminders+="}"
                    
            reminders+=']'
            reminders_json = json.loads(reminders.replace("'", '"'))
            return reminders_json
        
        return None
                
    def recurrence(self,event):

        if(event.recurrence != None):
            recurrence='RRULE:'

            if (event.recurrence.freq != None):
                recurrence+='FREQ='+event.recurrence.freq+';'
                
            if (event.recurrence.count != None):
                recurrence+='COUNT='+str(event.recurrence.count)+';'
                
            if (event.recurrence.interval != None):
                recurrence+='INTERVAL='+str(event.recurrence.interval)+';'
            
            if (event.recurrence.until != None):
                recurrence+='UNTIL='+str(event.recurrence.until)+';'
                
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

            return recurrence
        
        return None
    
    def emails(self, event):
        if(event.guests != []):
            emails=[]
            for guest in event.guests:
                emails.append( {'email': guest})
            
            return emails
        
        return None
    
    def start_time(self,event):
        year = event.time.eventStartDate.year
        month = event.time.eventStartDate.month
        day = event.time.eventStartDate.day

        hour = event.time.eventStartTime.hour
        minute = event.time.eventStartTime.minute

        start_time = datetime(year, month, day, hour, minute, tzinfo= pytz.timezone(event.time.eventTimeZone))
        return (start_time)
    
    def end_time(self,event):
        year = event.time.eventEndDate.year
        month = event.time.eventEndDate.month
        day = event.time.eventEndDate.day

        hour = event.time.eventEndTime.hour
        minute = event.time.eventEndTime.minute

        end_time = datetime(year, month, day, hour, minute, tzinfo= pytz.timezone(event.time.eventTimeZone))
        return (end_time)

    def event(self,event):    
        try:
            event_data = {
                'summary': event.title,
                'location': event.time.eventLocation,
                'description': event.description,
                'start': {
                    'dateTime': self.start_time(event).isoformat(),
                    'timeZone':  event.time.eventTimeZone,
                },
                'end': {
                    'dateTime': self.end_time(event).isoformat(),
                    'timeZone':  event.time.eventTimeZone,
                },
                'recurrence': [
                    self.recurrence(event)
                ],
                'attendees': self.emails(event)
                ,
                'reminders': {
                    'useDefault': self.setDefaultForReminders(event),
                    'overrides': self.create_reminders(event)
                },
                'visibility': event.visibility,
                'guestsCanSeeOtherGuests': event.guestsCanSeeOtherGuests,
                'guestsCanInviteOthers': event.guestsCanInviteOthers,
                'status': event.status
                }
        
            return event_data
        
        except HTTPError as error:
            print('An error occurred:', error)
            return None


    def insert_event(self, calendar_service, calendar_model):

        for event in calendar_model.events:
            event_data = self.event(event)
            if (event_data != None):
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