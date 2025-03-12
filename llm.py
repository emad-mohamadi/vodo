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
            messages=self.history[:2] + [{"role": role, "content": prompt}],
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
            Based on the information add 1 to 3 related tags for the task. Choose your recommended tags from this list but don't give same tags as which the task already has:
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
        prompt3 = """You are a personal productivity coach helping users manage their tasks and improve their productivity. Your responses will be embedded in an application.

I will provide task data in the following format for each task:

Name: Task title  
Description: A brief explanation of the task  
Date and Time: Scheduled execution time (ISO 8601 format)  
Expected Duration: User's estimate of task duration (in minutes)  
Repeat: Recurrence pattern ('Daily', 'Weekly', 'Monthly', 'Yearly', or empty if not recurring)  
Project: A category assigned by the user, optionally with a description  
Tags: Keywords categorizing the task (space-separated)  
Done?: 'Yes' or 'No' (if 'No', the following properties are omitted)  
Completed At: Actual completion timestamp (ISO 8601 format)  
Real Duration: Actual time spent (in minutes)  
Feedback: User satisfaction rating (1-5)  
User Comment: Optional remarks about task completion  

Your Tasks:
1. Analyze the user's behavior and detect interests by examining:  
   - Postponed tasks (tasks rescheduled or repeatedly left incomplete)  
   - Feedback ratings and user comments  
   - Progress in each project (ratio of completed to pending tasks)  

2. Identify behavioral patterns and habit cycles, if any.

3. Generate a personalized 3-4 paragraph review of the user's productivity patterns, including:  
   - Suggestions for improving efficiency and consistency  
   - Encouragement based on progress  

4. Recommend 3 tasks based on:  
   - The user's detected interests  
   - Available free time (based on scheduled and completed tasks)  

Format your response recommendations as a JSON objects (and nothing else):
It concludes the paragraphs; the keys are "title" and "text" and the new tasks; the keys are: "name", "description", "datetime", "expected_duration", "repeat", "project", "tags":

{
  "title": "Your paragraphs title",
  "text": "Your paragraphs",
  "tasks": [
    {
      "name": "Task 1 title",
      "description": "Task 1 description",
      "datetime": "Task 1 datetaime",
      "expected_duration": "minutes integer",
      "repeat": "daily, weekly, monthly or yearly",
      "project": "a user-created project name",
      "tags": "choose from user-created tags"
    },
    {
      "name": "Task 2 title",
      "description": "Task 2 description",
      "datetime": "Task 1 datetaime",
      "expected_duration": "minutes integer",
      "repeat": "daily, weekly, monthly or yearly",
      "project": "a user-created project name",
      "tags": "choose from user-created tags"
    },
    {
      "name": "Task 3 title",
      "description": "Task 3 description",
      "datetime": "Task 1 datetaime",
      "expected_duration": "minutes integer",
      "repeat": "daily, weekly, monthly or yearly",
      "project": "a user-created project name",
      "tags": "choose from user-created tags"
    }
  ]
}

Ensure your suggestions align with the user's goals, habits, and productivity trends.

I will send you the data and you send me the response (exactly in the format I mentioned)
"""

        response = self.chat(
            prompt=tasks_data
        )
        
        return response

    def save_history(self):
        self.data.table("users").update(
            {
                "history": self.history
            }
        ).eq("id", self.id).execute()


# assistant = AI()
# print(assistant.chat(prompt="hello"))
