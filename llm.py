from openai import OpenAI
from os import environ


def chat(query: str, model='gpt-4o', temprature=1) -> str:

    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=environ.get('GITHUB_TOKEN'),
    )

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "",
            },
            {
                "role": "user",
                "content": query,
            }
        ],
        model=model,
        temperature=temprature,
        max_tokens=4096,
        top_p=1
    )

    return response.choices[0].message.content
