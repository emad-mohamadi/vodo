from openai import OpenAI
from os import environ
from uuid import uuid1
import json


class AI:
    def __init__(self, id=uuid1().__str__()):
        self.id = id
        self.client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=environ.get("GITHUB_TOKEN"),
        )
        try:
            with open(f"{self.id}.json", "r") as file:
                self.history = json.load(file)
        except:
            self.history = [{"role": "system", "content": ""}]
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
            {"role": "assistant",
                "content": response.choices[0].message.content}
        )
        self.save_history()
        return self.history[-1]['content']

    def save_history(self):
        with open(f"{self.id}.json", "w") as file:
            file.write(json.dump(self.history, indent=4))
        return
