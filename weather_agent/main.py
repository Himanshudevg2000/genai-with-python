from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import requests

load_dotenv()

gemini_api_key=os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("❌ GEMINI_API_KEY is missing. Please set it in your .env file.")


client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

def get_weather(city: str):
    url =  f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)

    if(response.status_code == 200):
        return f"The weather in {city} is {response.text}"
    
    return "Something went wrong"

def main():
    user_query = input("👉 ")

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role":"user", "content": user_query}
        ]
    )
    print(f"response - {response.choices[0].message.content} ")

# main()

print(get_weather("bhopal")) 