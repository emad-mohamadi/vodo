from datetime import datetime as dt
from supabase import Client
from os import environ


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

    def add_task(self, task: Task, id: int):
        response = self.table("data").select("tasks").eq("id", id).execute()
        self.table("data").update(
            {
                "tasks":
                    response.data[0]["tasks"] + [task.__repr__()],
            }
        ).eq("id", id).execute()
        return

    def check_task(self, index: int, id: int):
        response = self.table("data").select("tasks").eq("id", id).execute()
        response.data[0]["tasks"][index]["completed"] = not response.data[0]["tasks"][index]["completed"]
        self.table("data").update(
            {
                "tasks":
                    response.data[0]["tasks"],
            }
        ).eq("id", id).execute()
        return
