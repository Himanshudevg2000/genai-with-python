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

# few shot promting - The model is provided with few examples - before asking it to generates an response
SYSTEM_PROMPT= """
    You are an expert of Coding, if someone asks anything which is not related to coding - then say i am expert in coding and cannot answer about this.

    Example:

    Q: Hey Can you create an sum of numbers ?
    A: def (num1, num2):
            return num1 + num2

    Q: Create while loop?
    A: while (condition):
        return value as per the questions they asked.
    
    Q: Can you teach me how to create an tutorial ?
    A: Sorry, I am an expert in coding


"""

response = client.chat.completions.create(
    model="gemini-2.5-flash",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        { "role": "user", "content": "Hello, I am Himanshu devgade! Nice to meet you, make a gym plan for me"}
    ]
)

print(response.choices[0].message.content)