import os

import requests


API_URL = "https://ollama.com/api/chat"
HEADERS = {"Authorization": "Bearer " + os.environ["OLLAMA_API_KEY"]}

tool_schema = {
    "type": "function",
    "function": {
        "name": "add2",
        "description": "Use this when the user wants to add two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "arg1": {"type": "string", "description": "the first number to add"},
                "arg2": {"type": "string", "description": "the second number to add"}
                
            },
            "required": ["arg1", "arg2"]
        }
    }
}

def agent(messages):
    tools = [tool_schema]

    payload = {
        "model": "gpt-oss:120b",
        "messages": messages,
        "stream": False,
        "tools": tools,
    }
    response = requests.post(
        API_URL,
        headers=HEADERS,
        json=payload,
        timeout=300,
    )
    response.raise_for_status()
    data = response.json()

    import pprint
    print = pprint.pprint
    print(data)

    message = data["message"]

    if "tool_calls" in message: 
        print("we have tool calls")
        tool_calls = message["tool_calls"]
        tool_calls = tool_calls[0]
        print(tool_calls)

        function_name = tool_calls["function"]["name"]
        function_arguments = tool_calls["function"]["arguments"]

        if function_name == "add2":
            arg1 = int(function_arguments["arg1"])
            arg2 = int(function_arguments["arg2"])
            print(f"function_name: {function_name}")
            print(f"arg1: {arg1}")
            print(f"arg2: {arg2}")

            output = arg1 + arg2
            print(output)

        if function_name == "get_weather": 
            
    else: 
        print("womp womp, no tool calls")
    return data["message"]["content"]


    

messages = [{"role": "user", "content": "Add 2 and 3"}]
print(agent(messages))