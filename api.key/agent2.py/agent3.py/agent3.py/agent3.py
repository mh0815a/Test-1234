import os
import glob
import subprocess
import requests

API_URL = "https://ollama.com/api/chat"
HEADERS = {"Authorization": "Bearer " + os.environ["OLLAMA_API_KEY"]}

read_file_tool_schema = {
    "type": "function",
    "function": {
        "name": "read_file",
"description": "Use this when the user wants read a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "the path of the file to read"}
            },
            "required": ["path"]
        }
    }       
}   

list_files_schema = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "Use this when the user wants to list files in the current working directory by default, or in a named directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "the path of the directory on which to list the files."}
            },
            "required": []
        }
    }
}


"description": "Use this when the user wants to list files in the current
working directory by default, or in a named directory.",
"parameters": {
"type": "object",
"properties": {
"path": {"type": "string", "description": "the path of the
directory on which to list the files."}
},
"required": []
}
}
}
write_file_tool_schema = {
"type": "function",
"function": {
"name": "write_file",
"description": "Use this when the user wants write a file.",
"parameters": {
"type": "object",
"properties": {
"path": {"type": "string", "description": "the path with filename
and extension of the file to write. Only .txt and .py."},
"content": {"type": "string", "description": "the contents of the
file."}
},
"required": ["path", "content"]
}
}
}
run_python_schema = {
"type": "function",
"function": {
"name": "run_python_file",
"description": "Use this when the user wants to run a python file",
"parameters": {
"type": "object",
"properties": {
"path": {"type": "string", "description": "The path of the python
file to run"},
},
"required": ["path"]
}
}
}
search_web_schema = {
"type": "function",
"function": {
"name": "search_web",
"description": "Use this to search the web",
"parameters": {
"type": "object",
"properties": {
"query": {"type": "string", "description": "The search query"},
},
"required": ["query"]
}
}
}
def search_web(query):
payload = {
"query": query
}
response = requests.post(
"https://ollama.com/api/web_search",
headers=HEADERS,
json=payload,
timeout=300,)
return response.json()
def agent(messages):
tools = [
read_file_tool_schema, list_files_schema, write_file_tool_schema,
run_python_schema, search_web_schema
]
payload = {
"model": "deepseek-v4.1-flash:cloud",
"messages": messages,
"stream": False,
"tools": tools
}
response = requests.post(
API_URL,
headers=HEADERS,
json=payload,
timeout=300,
)
response.raise_for_status()
data = response.json()
message = data["message"]
return message
import base64
with open("calculator/images.jpeg", "rb") as f:
img_b64 = base64.b64encode(f.read()).decode("utf-8")
tool_called = True
messages = [
{"role": "user",
"content": "What is the minimum drinking age in DC? use web search... write
the output to a file and cite sources",
}
]
while tool_called:
message = agent(messages)
print(message)
tool_called = "tool_calls" in message
if tool_called:
print("tool called!")
tool_calls = message["tool_calls"]
tool_call = tool_calls[0]
function_name = tool_call["function"]["name"]
function_arguments = tool_call["function"]["arguments"]
if function_name == "search_web":
output = "sample fake output"
query = function_arguments["query"]
results = search_web(query)
import json
output = json.dumps(results)
if function_name == "list_files":
path = "."
if "path" in function_arguments:
path = function_arguments["path"]
print(f"arguments for list_files: {path}")
#files = "\n".join(os.listdir(path))
files = glob.glob(f"{path}/*")
output = files
if function_name == "read_file":
path = function_arguments["path"]
with open(path, "r") as file:
file_content = file.read()
output = file_content
if function_name == "write_file":
path = function_arguments["path"]
content = function_arguments["content"]
with open(path, "w") as file:
file.write(content)
output = f"File written to {path} with content: {content}"
if function_name == "run_python_file":
path = function_arguments["path"]
# Run the command and capture output
result = subprocess.run(['python', path], capture_output=True,
text=True, check=True)
# Access the captured stdout
output = f"output of python {path}: {result}"
# if function_name == "add2":
# arg1 = int(function_arguments["arg1"])
# arg2 = int(function_arguments["arg2"])
# print(f"function_name: {function_name}")
# print(f"arg1: {arg1}")
# print(f"arg2: {arg2}")
# output = arg1 + arg2
tool_message = {
"role": "tool",
"content": f"The output of tool {function_name} is: {output}"
}
messages.append(tool_message)
else:
ai_message = {
"role": message["role"],
"content": message["content"]
}
messages.append(ai_message)
last_message = messages[-1]
import pprint
printer = pprint.pprint
# printer(last_message)
print