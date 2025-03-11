from openai import OpenAI
from os import environ
from logic import DataBase
import json


class AI:
    def __init__(self, id=1, save=True):
        self.id = id
        self.save = save
        self.client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=environ.get("GITHUB_TOKEN"),
        )
        self.data = DataBase()
        self.history = self.data.table("users").select(
            "history").eq("id", self.id).execute().data[0]["history"] if save else []
        # try:
        #     with open(f"{self.id}.json", "r") as file:
        #         self.history = json.load(file)
        # except:
        return

    def chat(self, prompt: str, role="user", model='gpt-4o', temprature=1) -> str:
        self.history.append({"role": role, "content": prompt})
        response = self.client.chat.completions.create(
            messages=self.history,
            model=model,
            temperature=temprature,
            max_tokens=4096,
            top_p=1
        )
        self.history.append(
            {
                "role": "assistant",
                "content": response.choices[0].message.content,
            }
        )
        if self.save:
            self.save_history()
        return self.history[-1]['content']

    def get_tags(self, task_data):
        prompt1 = """
            Here is some information about a task which user is going to add.
        """
        prompt2 = """
            Based on the information add 1 to 3 related tags for the task. Choose your recommended tags from this list but don't give duplicate tags as which the task already has:
            tags = [
                "Work", "Personal", "Urgent", "Home", "Errand", "Health", "Finance", "Shopping",
                "Study", "Meeting", "Project", "Travel", "Appointment", "Leisure",
                "Fitness", "Family", "Social", "Research", "Creative", "Planning", "Review",
                "Writing", "Design", "Development", "Analysis", "Entertainment", "Reminder",
                "Learning", "Maintenance"
            ]
            Just send me the tags splitted by spaces.
            """
        response = self.chat(
            prompt=prompt1+"\n"+task_data+"\n"+prompt2,
        )
        return response.split()

    def get_review(self, tasks_data):
        prompt1 = """pass"""#TODO

        pass

    def save_history(self):
        self.data.table("users").update(
            {
                "history": self.history
            }
        ).eq("id", self.id).execute()


# assistant = AI()
# print(assistant.chat(prompt="hello"))
