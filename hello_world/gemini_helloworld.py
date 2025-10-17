from google import genai
import os

gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("❌ GEMINI_API_KEY is missing. Please set it in your .env file.")

client = genai.Client(
    api_key=gemini_api_key
)
response = client.models.generate_content(
    model='gemini-2.5-flash', contents="Explain how AI works in few words"
)

print(response.text)