from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key="api_key",
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": "You are an expert of Fitness, if someone asks anything which is not related to fitness - then say i am expert in fitness and cannot answer about this."},
        { "role": "user", "content": "Hello, I am Himanshu devgade! Nice to meet you, write a code for 2 and 3 table"}
    ]
)

print(response.choices[0].message.content)