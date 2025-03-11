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
        response = self.table("users").select(
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

    def get_tasks(self, user_id=1):
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
            repeat = task.get("repeat", "No repeat")

            if repeat != "No repeat" and task_datetime < today_end:
                print(task["name"])
                new_uuid = uuid1().__str__()
                self.table("tasks").update(
                    {
                        "repeat": "No repeat",
                        "uuid": new_uuid,
                    },
                ).eq("uuid", task["uuid"]).execute()
                task_ids.remove(task["uuid"])
                task_ids.append(new_uuid)

                new_time = task_datetime
                last = deepcopy(task)
                last.pop("created_at")
                last.pop("id")
                last["repeat"] = "No repeat"
                last["completed"] = False

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
                    task_ids.append(new_task["uuid"])
                    new_task.pop("created_at")
                    new_task.pop("id")
                    new_task["repeat"] = "No repeat"
                    new_task["completed"] = False
                    self.table("tasks").insert(new_task).execute()
                    last = deepcopy(new_task)

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

                new_task = deepcopy(last)
                new_task["datetime"] = datetime.isoformat(new_time)
                new_task["repeat"] = repeat
                print(new_task)
                self.table("tasks").insert(new_task).execute()

        self.table("users").update(
            {
                "tasks":
                    task_ids,
            }
        ).eq("id", user_id).execute()

        response = self.table("tasks").select("*").execute()
        tasks = [task for task in response.data if task["uuid"] in task_ids]

        for task in tasks:
            task_datetime = datetime.fromisoformat(task["datetime"])
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
