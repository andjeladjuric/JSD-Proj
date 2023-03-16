from datetime import datetime

class Tasks():
    def __find_list_by_title(self, tasklists, title):
        for list in tasklists:
            if list["title"] == title: return list

    def query_tasks_by_tasklist_and_status(self, calendar_model, tasks_service):
        found_tasks = []

        for rule in calendar_model.findTasks:
            title = rule.tasklist
            status = rule.status

            tasklists_result = tasks_service.tasklists().list().execute()
            tasklists = tasklists_result.get('items', [])
            completed_max = datetime.utcnow().isoformat() + 'Z' if status == 'completed' else None

            tasklist = self.__find_list_by_title(tasklists, title)
            tasks_result = tasks_service.tasks().list(
                tasklist=tasklist['id'],
                showCompleted=True,
                completedMax=completed_max
            ).execute()
            tasks = tasks_result.get('items', [])
            found_tasks.extend(tasks)
        
        for task in tasks:
            print("\n{} \n\tstatus: {} \n\tdue: {}".format(
                task['title'], task['status'], task['due']))

    def tasklist_data(self, tasklist):
        try:
            tasklist_data = {
                'title' : tasklist.title
            }
            return tasklist_data
        except:
            return None


    def create_new_tasklist(self, calendar_model, tasks_service):
        for tasklist in calendar_model.tasklists:
            tasklist_data = self.tasklist_data(tasklist)
            tasks_service.tasklists().insert(body=tasklist_data).execute()
        
        print(f"Tasklist is created!")

            
    def delete_tasklist(self, tasks_service, tasklist_name):
        tasklists_result = tasks_service.tasklists().list().execute()
        tasklists = tasklists_result.get('items', [])

        tasklist_id = None
        for tasklist in tasklists:
            if tasklist['title'] == tasklist_name:
                tasklist_id = tasklist['id']
                break

        if tasklist_id is not None:
            tasks_service.tasklists().delete(tasklist=tasklist_id).execute()
            print(f"Tasklist '{tasklist_name}' deleted successfully.")
        else:
            print(f"No tasklist found with name '{tasklist_name}'.")

    def start_time(self, tasks):
        year = tasks.date.year
        month = tasks.date.month
        day = tasks.date.day

        hour = tasks.time.hour
        minute = tasks.time.minute

        start_time = datetime(year, month, day, hour, minute, tzinfo=datetime.now(pytz.utc).astimezone().tzinfo)
        return (start_time)


    def task_data(self, task):
        try:
            task_data = {
                'title': task.title,
                'description': task.description,
                'start': {
                    'dateTime': self.start_time(task).isoformat(),
                },
            }
            return task_data
        except:
            return None

    def insert_task(self, tasks_service, calendar_model):
        for task in calendar_model.tasks:
            task_data = self.task_data(task)
            if (task_data != None):
                tasks_service.tasks().insert(tasklist='@default',body=task_data).execute()

