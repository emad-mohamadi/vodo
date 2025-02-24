from datetime import datetime as dt
from supabase import Client
from os import environ
from uuid import uuid1
from datetime import datetime

class Task:
    def __init__(self, name, description=None, category=None, datetime=None, repeat=None, duration=None):
        self.name = name
        self.description = description
        self.category = category
        self.completed = False
        self.tags = []
        self.datetime = datetime
        self.repeat = repeat
        self.duration = duration
        self.comment = None
        self.feedback = None
        self.created_at = dt.now().__str__()

    def __repr__(self):
        return {
            "created_at": self.created_at,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "completed": self.completed,
            "tags": self.tags,
            "duration": self.duration,
            "datetime": self.datetime,
            "repeat": self.repeat,
            "comment": self.comment,
            "feedback": self.feedback,
        }


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

        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        ongoing_tasks = {task["uuid"]: task for task in tasks if now < datetime.fromisoformat(task["create_time"])}
        today_tasks = {task["uuid"]: task for task in tasks if today_start <= datetime.fromisoformat(task["create_time"]) <= today_end}
        overdue_tasks = {task["uuid"]: task for task in tasks if now > datetime.fromisoformat(task["create_time"])}

        return ongoing_tasks, today_tasks, overdue_tasks
