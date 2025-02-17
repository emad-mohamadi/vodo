from datetime import datetime
from supabase import Client
from os import environ

# key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5mbm1jaGlnendoeWV2Y3h6Z3d5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzg5Mjg0ODEsImV4cCI6MjA1NDUwNDQ4MX0.82X66JQi3AaRNdzW8Zhg_0v5RKgElCAk8HXEym2gm5k"
# url = "https://nfnmchigzwhyevcxzgwy.supabase.co"


class DataBase(Client):
    def __init__(self, url=environ.get("SUPABASE_URL"), key=environ.get("SUPABASE_KEY")):
        super().__init__(url, key)

    def get_tasks(self):
        response = self.table('tasks').select('*').execute()
        return response.data


class Task:
    def __init__(self, id, name, description="", category="uncategorized"):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.completed = False
        self.created_at = datetime.now()

    def complete_toggle(self):
        self.completed = not self.completed
        return
