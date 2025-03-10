from supabase import Client
from os import environ
from uuid import uuid1
from datetime import datetime, timedelta, timezone


class DataBase(Client):
    def __init__(self, url=environ.get("SUPABASE_URL"), key=environ.get("SUPABASE_KEY")):
        super().__init__(url, key)

    def add_task(self, data, user_id):
        response = self.table("tasks").insert(data).execute()
        self.table("users").select(
            "tasks").eq("id", user_id).execute()
        self.table("users").update(
            {
                "tasks":
                    (response.data[0]["tasks"] or []) + [data["uuid"]],
            }
        ).eq("id", user_id).execute()
        return

    def edit_task(self, data, task_id):
        self.table("tasks").update(
            data
        ).eq("uuid", task_id).execute()
        return

    def delete_task(self, task_id, project_id=None, user_id=1):
        user = self.table("users").select("*").eq(
            "id", user_id).execute().data[0]
        user["tasks"].remove(task_id)
        self.table("users").update(
            {
                "tasks": user["tasks"],
            }
        ).eq("id", user_id).execute()
        self.table("tasks").delete().eq("uuid", task_id)

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
        response = self.table("projects").insert(data).execute()
        response = self.table("users").select(
            "projects").eq("id", user_id).execute()
        self.table("users").update(
            {
                "projects":
                    (response.data[0]["projects"] or []) + [data["uuid"]],
            }
        ).eq("id", user_id).execute()
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

    def get_tasks(self, user_id):
        task_ids_response = self.table("users").select(
            "tasks").eq("id", user_id).execute()
        task_ids = task_ids_response.data[0]["tasks"] if task_ids_response.data else [
        ]

        response = self.table("tasks").select("*").execute()
        tasks = [task for task in response.data if task["uuid"] in task_ids]

        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(
            hour=23, minute=59, second=59, microsecond=999999)

        ongoing_tasks = {}
        today_tasks = {}
        overdue_tasks = {}

        for task in tasks:
            task_datetime = datetime.fromisoformat(task["datetime"])
            repeat = task.get("repeat", "none")  # Default is "none" if missing

            # # Handle repeating tasks
            # if repeat != "none" and task_datetime < today_end:
            #     if repeat == "daily":
            #         task_datetime += timedelta(days=1)
            #     elif repeat == "weekly":
            #         task_datetime += timedelta(weeks=1)
            #     elif repeat == "monthly":
            #         task_datetime += relativedelta(months=1)
            #     elif repeat == "yearly":
            #         task_datetime += relativedelta(years=1)

            # Categorize tasks
            if task_datetime > today_end:
                ongoing_tasks[task["uuid"]] = task
            elif today_start <= task_datetime <= today_end:
                today_tasks[task["uuid"]] = task
            else:
                overdue_tasks[task["uuid"]] = task

        return ongoing_tasks, today_tasks, overdue_tasks

    def get_projects(self, user_id):
        project_ids_response = self.table("users").select(
            "projects").eq("id", user_id).execute()
        project_ids = project_ids_response.data[0]["projects"] if project_ids_response.data else [
        ]

        response = self.table("projects").select("*").execute()
        projects = [
            project for project in response.data if project["uuid"] in project_ids]

        return projects


# d = DataBase()
# print(d.table("users").select(
#     "history").eq("id", 1).execute().data[0]["history"])
