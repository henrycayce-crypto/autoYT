from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv("API_key.env")

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.getenv("GITHUB_TOKEN")
)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "user", "content": "say hello"}
    ]
)

print(response.choices[0].message.content)