from dotenv import load_dotenv
import os
from openai import OpenAI
import json

load_dotenv()

gemini_api_key=os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("❌ GEMINI_API_KEY is missing. Please set it in your .env file.")


client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

SYSTEM_PROMPT = """
    You are an AI expert which helps in resolving coding queries using chain of thought.
    You work on START, PLAN and OUTPUT.
    You need to first make an plan which needs to be done. Planning can be done in muliple steps.
    Once you think enough PLAN has been done, then finally you gives an OUTPUT.

    RULES
    - Strictly follow Json OUTPUT format.
    - Strictly return **only one** JSON object per message, not an array.
    - Each Step at a time.
    - The sequence of steps is - START (where user inputs an query), PLAN(it can be in multiple steps, think step by step for the query) and then OUTPUT(which is going to be displayed to the user)
    
    OUTPUT Json Format - 
    { "step": "START" | "PLAN" | "OUTPUT", "content": "string }

    Examples
    START: Hey Can you solve 2 + 2 * 5 / 10 - 55 + 360 ?
    PLAN: { "step": "PLAN", "content": "User wants to solve maths problem"}.
    PLAN: { "step": "PLAN", "content": "This maths problem can be solved with maths BODMAS rules"}.
    PLAN: { "step": "PLAN", "content":"There are no brackets or orders, so do multiplication and division left to right:
            First compute 2 * 5 = 10.
            The expression becomes: 2 + 10 / 10 - 55 + 360."}
    PLAN:  { "step": "PLAN", "content": " Next compute 10 / 10 = 1.
            Now: 2 + 1 - 55 + 360.
            Now do addition and subtraction left to right:"}
    PLAN:  { "step": "PLAN", "content": " 2 + 1 = 3 → expression: 3 - 55 + 360.
            3 - 55 = -52 → expression: -52 + 360.
            -52 + 360 = 308."}
    OUTPUT: { "step": "PLAN", "content": "308"}
    

"""

user_query = input("👉 ")
message_history = [ {"role": "system", "content": SYSTEM_PROMPT }]
message_history.append(
    {"role": "user", "content": user_query}
)

while True:
    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        response_format={"type": "json_object"},
        messages=message_history
    )

    raw_result = response.choices[0].message.content
    message_history.append({"role": "assistant", "content": raw_result})
    parsed_result = json.loads(raw_result)

    if parsed_result.get("step") == "START":
        print("🔥 ", parsed_result.get("content"))
        continue

    if parsed_result.get("step") == "PLAN":
        print("🧠 ", parsed_result.get("content"))
        continue

    if parsed_result.get("step") == "OUTPUT":
        print("🤖 ", parsed_result.get("content"))
        break
