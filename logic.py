from supabase import Client
from os import environ
from uuid import uuid1
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta  

class DataBase(Client):
    def __init__(self, url=environ.get("SUPABASE_URL"), key=environ.get("SUPABASE_KEY")):
        super().__init__(url, key)

    def add_task(self, data, user_id):
        task_id = uuid1().__str__()
        data["uuid"] = task_id
        response = self.table("tasks").insert(data).execute()
        response = self.table("users").select("tasks").eq("id", user_id).execute()
        self.table("users").update(
            {
                "tasks":
                    (response.data[0]["tasks"] or []) + [task_id],
            }
        ).eq("id", user_id).execute()
        return

    def check_task(self, uuid, check: bool, id: int):
        self.table("tasks").update(
            {
                "completed":
                    check,
            }
        ).eq("uuid", uuid).execute()
        return


    def get_tasks(self, user_id):
        task_ids_response = self.table("users").select("tasks").eq("id", user_id).execute()
        task_ids = task_ids_response.data[0]["tasks"] if task_ids_response.data else []

        response = self.table("tasks").select("*").execute()
        tasks = [task for task in response.data if task["uuid"] in task_ids]

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        ongoing_tasks = {}
        today_tasks = {}
        overdue_tasks = {}

        for task in tasks:
            task_datetime = datetime.fromisoformat(task["datetime"])
            repeat = task.get("repeat", "none")  # Default is "none" if missing

            # Handle repeating tasks
            if repeat != "none":
                while task_datetime < today_start:
                    if repeat == "daily":
                        task_datetime += timedelta(days=1)
                    elif repeat == "weekly":
                        task_datetime += timedelta(weeks=1)
                    elif repeat == "monthly":
                        task_datetime += relativedelta(months=1)
                    elif repeat == "yearly":
                        task_datetime += relativedelta(years=1)

            # Categorize tasks
            if task_datetime > today_end:
                ongoing_tasks[task["uuid"]] = task
            elif today_start <= task_datetime <= today_end:
                today_tasks[task["uuid"]] = task
            else:
                overdue_tasks[task["uuid"]] = task

        return ongoing_tasks, today_tasks, overdue_tasks
