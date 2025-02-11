from openai import OpenAI
from os import environ

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=environ.get('GITHUB_TOKEN'),
)

query = ""
while query != "exit":
    query = input("> ")

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
        model="gpt-4o",
        temperature=1,
        max_tokens=4096,
        top_p=1
    )

    print("+ " + response.choices[0].message.content)
