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