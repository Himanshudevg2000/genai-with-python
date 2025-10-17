from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("❌ GEMINI_API_KEY is missing. Please set it in your .env file.")

client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

# zero shot promting - the model is given a direct question or task without prior examples 
SYSTEM_PROMPT= "You are an expert of Fitness, if someone asks anything which is not related to fitness - then say i am expert in fitness and cannot answer about this."

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        { "role": "user", "content": "Hello, I am Himanshu devgade! Nice to meet you, write a code for 2 and 3 table"}
    ]
)

print(response.choices[0].message.content)