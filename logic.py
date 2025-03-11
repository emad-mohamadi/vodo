from supabase import Client
from os import environ
from uuid import uuid1
from datetime import datetime, timedelta, timezone
from copy import deepcopy


class DataBase(Client):
    def __init__(self, url=environ.get("SUPABASE_URL"), key=environ.get("SUPABASE_KEY")):
        super().__init__(url, key)

    def add_task(self, data, user_id=1):
        self.table("tasks").insert(data).execute()
        return

    def edit_task(self, data, task_id):
        self.table("tasks").update(
            data
        ).eq("uuid", task_id).execute()
        return

    def delete_task(self, task_id, project_id=None, user_id=1):
        self.table("tasks").delete().eq("uuid", task_id).execute()

        if not project_id:
            return True
        project_tasks = self.table("projects").select(
            "tasks"
        ).eq(
            "uuid", project_id
        ).execute().data[0]["tasks"]
        project_tasks.remove(task_id)
        self.table("projects").update(
            {
                "tasks": project_tasks,
            }
        ).eq("uuid", project_id).execute()
        return True

    def add_project(self, data, user_id):
        self.table("projects").insert(data).execute()
        return

    def add_to_project(self, project_id, task_id):
        response = self.table("projects").select(
            "tasks").eq("uuid", project_id).execute()
        self.table("projects").update(
            {
                "tasks":
                    (response.data[0]["tasks"] or []) + [task_id],
            }
        ).eq("uuid", project_id).execute()
        return

    def check_task(self, uuid, check: bool, id: int):
        self.table("tasks").update(
            {
                "completed":
                    check,
            }
        ).eq("uuid", uuid).execute()
        return

    def get_tasks(self):
        response = self.table("tasks").select("*").execute()
        tasks = response.data

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(
            hour=23, minute=59, second=59, microsecond=999999)

        ongoing_tasks = {}
        today_tasks = {}
        overdue_tasks = {}

        for task in tasks:
            task_datetime = datetime.fromisoformat(task["datetime"])
            repeat = task["repeat"]

            if repeat != "No repeat" and task_datetime < today_end:
                print(task["name"])
                self.table("tasks").update(
                    {
                        "repeat": "No repeat",
                    },
                ).eq("uuid", task["uuid"]).execute()

                new_time = task_datetime

                if repeat == "Daily":
                    new_time += timedelta(days=1)
                elif repeat == "Weekly":
                    new_time += timedelta(weeks=1)
                elif repeat == "Monthly":
                    new_time += timedelta(days=30)
                elif repeat == "Yearly":
                    new_time += timedelta(days=365)
                while new_time < today_end:
                    new_task = deepcopy(task)
                    new_task["datetime"] = datetime.isoformat(new_time)
                    new_task["uuid"] = uuid1().__str__()
                    new_task.pop("created_at")
                    new_task.pop("id")
                    new_task.pop("real_duration")
                    new_task.pop("feedback")
                    new_task.pop("completed_at")
                    new_task["repeat"] = "No repeat"
                    new_task["completed"] = False
                    self.table("tasks").insert(new_task).execute()

                    if repeat == "Daily":
                        new_time += timedelta(days=1)
                    elif repeat == "Weekly":
                        new_time += timedelta(weeks=1)
                    elif repeat == "Monthly":
                        new_time += timedelta(days=30)
                    elif repeat == "Yearly":
                        new_time += timedelta(days=365)
                    else:
                        break

                new_task = deepcopy(task)
                new_task["datetime"] = datetime.isoformat(new_time)
                new_task["uuid"] = uuid1().__str__()
                new_task.pop("created_at")
                new_task.pop("id")
                new_task.pop("real_duration")
                new_task.pop("feedback")
                new_task.pop("completed_at")
                new_task["repeat"] = repeat
                new_task["completed"] = False
                self.table("tasks").insert(new_task).execute()

        response = self.table("tasks").select("*").execute()
        tasks = response.data

        for task in tasks:
            task_datetime = datetime.fromisoformat(task["datetime"])
            if task_datetime > today_end:
                ongoing_tasks[task["uuid"]] = task
            elif today_start <= task_datetime <= today_end:
                today_tasks[task["uuid"]] = task
            else:
                overdue_tasks[task["uuid"]] = task

        return ongoing_tasks, today_tasks, overdue_tasks

    def get_projects(self):
        response = self.table("projects").select("*").execute()
        projects = response.data

        return projects


d = DataBase()
d.get_tasks()
