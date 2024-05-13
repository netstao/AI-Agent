from openai import OpenAI
from dotenv import load_dotenv
# Load environment variables from openai.env file
load_dotenv()
client = OpenAI(api_key="sk-b1bc99f27b4641d2a32801cd3feaae53", base_url="https://api.deepseek.com/v1")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "给我小孩讲个睡前故事"},
    ]
)

print(response.choices[0].message.content)