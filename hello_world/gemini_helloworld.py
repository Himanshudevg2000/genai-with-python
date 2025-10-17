from google import genai

client = genai.Client(
    api_key="api_key"
)

response = client.models.generate_content(
    model='gemini-2.5-flash', contents="Explain how AI works in few words"
)

print(response.text)