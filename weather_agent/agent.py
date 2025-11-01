from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import requests
import re
import time
from openai import RateLimitError
from pydantic import BaseModel, Field
from typing import Optional
import subprocess

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
    Tou can also call a tool if required from the list of available tools.
    For every tool call wait for the observe step which is the output from the called tool.

    RULES
    - Strictly follow Json OUTPUT format.
    - Strictly return **only one** JSON object per message, not an array.
    - Each Step at a time.
    - The sequence of steps is - START (where user inputs an query), PLAN(it can be in multiple steps, think step by step for the query) and then OUTPUT(which is going to be displayed to the user)
    - When using create_file, always send both "file_path" and "content" as keys inside input. Example:
    { "step": "TOOL", "tool": "create_file", "input": {"file_path": "todo/index.html", "content": "<html>...</html>"} }
    - Similarly, for update_file, include {"file_path": "...", "new_content": "...", "mode": "overwrite"}.
    
    OUTPUT Json Format - 
    { "step": "START" | "PLAN" | "TOOL" | "OUTPUT", "content": "string", "tool": "string", "input": "string" }

    Available Tools:
    - get_weather(city: str): Takes a city name and returns the weather info.
    - run_command(cmd: str): Executes a Linux command.
    - create_file(file_path: str, content: str): Creates a new file with optional content.
    - create_folder(folder_path: str): Creates a new folder (recursively if needed).
    - update_file(file_path: str, new_content: str, mode: str = "append"): Updates or overwrites a file.
    - run_windows_command(cmd: str): Executes a Windows command and returns output.
    
    Notes:
    - When user asks for file/folder operations, prefer using the respective tool.
    - Use run_windows_command for commands like 'dir', 'echo', 'type', 'mkdir', etc.

    Example 1:
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

    Example 2:
    START: What is te weather of bhopal ?
    PLAN: { "step": "PLAN", "content": "Seems like user is intersted in weather info of bhopal city in india"}.
    PLAN: { "step": "PLAN", "content": "Lets see if we have any available tools to get weather info from the list of available tools"}.
    PLAN: { "step": "PLAN", "content":"Great we have get_weather tool available for this query "}
    PLAN:  { "step": "PLAN", "content": "I need to call get_weather tool for bhopal as input parameter for the city"}
    PLAN:  { "step": "TOOL", "tool": "get_weather", "input": "bhopal"}
    PLAN:  { "step": "OBSERVE", "tool": "get_weather", "output": "The temp of bhopal is cloudy with 22 degree celcius"}
    PLAN:  { "step": "PLAN", "content": "Great, I got the weather info about bhopal."}
    OUTPUT: { "step": "OUTPUT", "content": "The current weather in bhopal is 22 degree Celcius with some cloudy sky"}
    
"""

class MyOutputFormat(BaseModel):
    step: str = Field(..., description="The ID of the step. Example: PLAN, OUTPUT, TOOL, etc")
    content: Optional[str] = Field(None, description="The optional string content for the step")
    tool: Optional[str] = Field(None, description="The ID of the tool to call.")
    input: Optional[str] = Field(None, description="The input params for the tool")

def run_command(cmd: str):
    result = os.system(cmd)
    return result

def run_windows_command(cmd: str):
    """Executes a Windows command and returns its output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return f"💻 Command executed successfully:\n{result.stdout}"
        else:
            return f"⚠️ Command failed:\n{result.stderr}"
    except Exception as e:
        return f"❌ Error executing command: {str(e)}"

def create_file(file_path: str, content: str = ""):
    """Creates a new file with optional content."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ File created successfully at {file_path}"
    except Exception as e:
        return f"❌ Failed to create file: {str(e)}"

def create_folder(folder_path: str):
    """Creates a new folder (and parents if missing)."""
    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"📁 Folder created at {folder_path}"
    except Exception as e:
        return f"❌ Failed to create folder: {str(e)}"

def update_file(file_path: str, new_content: str, mode: str = "append"):
    """
    Updates an existing file.
    mode: "append" (default) adds new content, "overwrite" replaces entire content.
    """
    try:
        if mode == "overwrite":
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        else:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write("\n" + new_content)
        return f"📝 File {file_path} updated successfully in {mode} mode."
    except Exception as e:
        return f"❌ Failed to update file: {str(e)}"


def get_weather(city: str):
    url =  f"https://wttr.in/{city.lower()}?format=%C+%t"
    response = requests.get(url)

    if(response.status_code == 200):
        return f"The weather in {city} is {response.text}"
    
    return "Something went wrong"

def run_command(cmd: str):
    result = os.system(cmd)
    return result

available_tools = {
    "get_weather": get_weather,
    "run_command": run_command,
    "create_file": create_file,
    "create_folder": create_folder,
    "update_file": update_file,
    "run_windows_command": run_windows_command
}

user_query = input("👉 ")
message_history = [ {"role": "system", "content": SYSTEM_PROMPT }]
message_history.append(
    {"role": "user", "content": user_query}
)

while True:
    try:
        response = client.chat.completions.parse(
            model="gemini-2.5-flash",
            response_format=MyOutputFormat,
            messages=message_history
        )
    
    except RateLimitError as e:
        # Parse retry delay (e.g. "Please retry in 49.177843617s")
        match = re.search(r"retry in ([\d.]+)s", str(e))
        delay = float(match.group(1)) if match else 60
        print(f"⚠️ Rate limit hit. Waiting {delay:.1f}s before retrying...")
        time.sleep(delay)
        continue

    raw_result = response.choices[0].message.content
    message_history.append({"role": "assistant", "content": raw_result})
    # parsed_result = json.loads(raw_result)
    try:
        parsed_result = response.choices[0].message.parsed
    except json.JSONDecodeError:
        print("⚠️ Invalid JSON from model:", raw_result)
        break

    if parsed_result.step == "START":
        print("🔥 ", parsed_result.content)
        continue

    if parsed_result.step == "TOOL":
        tool_to_call = parsed_result.tool
        tool_input = parsed_result.input
        print(f"⚒️ , {tool_to_call} ({tool_input})")

        # 🧠 Handle JSON input (dict) or plain string gracefully
        tool_func = available_tools.get(tool_to_call)

        if isinstance(tool_input, str):
            tool_response = tool_func(tool_input)
        elif isinstance(tool_input, dict):
            tool_response = tool_func(**tool_input)
        else:
            tool_response = f"❌ Invalid tool input format: {tool_input}"

    if parsed_result.step == "PLAN":
        print("🧠 ", parsed_result.content)
        continue

    if parsed_result.step == "OUTPUT":
        print("🤖 ", parsed_result.content)
        break

    time.sleep(4) 