from datetime import datetime
from tzlocal import get_localzone_name
import pytz, json
from requests import HTTPError

class Events():
    def check_if_timezone_is_valid(self, calendar_model):
        timezones = set(pytz.all_timezones)

        for event in calendar_model.events:
            if (event.time.eventTimeZone != None):
                if (not event.time.eventTimeZone in timezones):
                    return False
            
        return True

    def check_recurrence_rule(self, calendar_model):
        for event in calendar_model.events:
            if (event.recurrence != None):
                if (event.recurrence.freq == 'DAILY' and event.recurrence.interval != None and event.recurrence.byDay != []):
                    return False
                
                if (event.recurrence.freq == 'WEEKLY' and event.recurrence.byDay != [] and event.recurrence.byMonthDay != []):
                    return False

                if (event.recurrence.freq == 'YEARLY' and event.recurrence.byDay != [] and event.recurrence.byMonthDay != []):
                    return False

        return True

    def setDefaultForReminders(self,event):
        if (event.notifications != []):
            return False
        return True
    
    def create_reminders(self,event):
        if (event.notifications != []):
            reminders = []

            for notification in event.notifications:
                interval = 0
                if notification.interval == 'hours':
                    interval = notification.number * 60
                elif notification.interval == 'days':
                    interval = notification.number * 24 * 60
                elif notification.interval == 'weeks':
                    interval = notification.number * 7 * 24 * 60
                else:
                    interval = notification.number

                reminder = {
                    "method": notification.method,
                    "minutes": interval
                }

                reminders.append(reminder)

            return reminders
        
        return None
                
    def recurrence(self,event):
        if(event.recurrence != None):
            recurrence='RRULE:'

            if (event.recurrence.freq != None):
                recurrence+='FREQ='+event.recurrence.freq.upper()+';'
                
            if (event.recurrence.ends.count != None and event.recurrence.ends.count != 0):
                recurrence+='COUNT='+str(event.recurrence.ends.count)+';'
                
            if (event.recurrence.interval != None):
                recurrence+='INTERVAL='+str(event.recurrence.interval)+';'
            
            if (event.recurrence.ends.until != None):
                rule = event.recurrence.ends.until
                until_string = f'{rule.year}-{rule.month}-{rule.day}'
                until = datetime.strptime(until_string, "%Y-%m-%d")
                iso_date = until.strftime("%Y%m%dT%H%M%SZ")
                recurrence+='UNTIL='+str(iso_date)+';'
                
            if (event.recurrence.byMonth != []):
                months = []
                for element in event.recurrence.byMonth:
                    month_number = datetime.strptime(element, "%B").month
                    months.append(str(month_number))

                byMonth = ",".join(months)
                recurrence+='BYMONTH='+byMonth+';'

            if (event.recurrence.byMonthDay != []):
                byMonthDay = ",".join(str(element) for element in event.recurrence.byMonthDay)
                recurrence += 'BYMONTHDAY='+byMonthDay+';'

            elif (event.recurrence.byDay != []):
                days = []
                for element in event.recurrence.byDay:
                    if (element == 'saturday'):
                        days.append('ST')
                    else:
                        days.append(element[:2].upper())

                byDay = ",".join(days)
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

        if (event.time.eventTimeZone != None):
            start_time = datetime(year, month, day, hour, minute, tzinfo=pytz.timezone(event.time.eventTimeZone))
        else:
            start_time = datetime(year, month, day, hour, minute, tzinfo=datetime.now(pytz.utc).astimezone().tzinfo)

        return (start_time)
    
    def end_time(self,event):
        year = event.time.eventEndDate.year
        month = event.time.eventEndDate.month
        day = event.time.eventEndDate.day

        hour = event.time.eventEndTime.hour
        minute = event.time.eventEndTime.minute

        if (event.time.eventTimeZone != None):
            end_time = datetime(year, month, day, hour, minute, tzinfo=pytz.timezone(event.time.eventTimeZone))
        else:
            end_time = datetime(year, month, day, hour, minute, tzinfo=datetime.now(pytz.utc).astimezone().tzinfo)

        return (end_time)

    def event(self,event):
        
        try:
            event_data = {
                'summary': event.title,
                'location': event.time.eventLocation,
                'description': event.description,
                'start': {
                    'dateTime': self.start_time(event).isoformat()
                },
                'end': {
                    'dateTime': self.end_time(event).isoformat()
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

            if (event.time.eventTimeZone != None):
                event_data['end']['timeZone'] = event.time.eventTimeZone
                event_data['start']['timeZone'] = event.time.eventTimeZone
            else:
                event_data['end']['timeZone'] = get_localzone_name()
                event_data['start']['timeZone'] = get_localzone_name()

            return event_data
    
        except HTTPError as error:
            print('An error occurred:', error)
            return None


    def insert_event(self, calendar_service, calendar_model):
        for event in calendar_model.events:
            event_data = self.event(event)
            if (event_data != None):
                calendar_service.events().insert(calendarId="primary", body=event_data).execute()


    def query_events_by_rule(self, calendar_model, calendar_service):
        found_events = []
        owner = ''

        for rule in calendar_model.findEvents:
            owner = rule.owner
            
            if (rule.start != None and rule.end != None):
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
            else:
                events_result = calendar_service.events().list(
                    calendarId='primary',
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