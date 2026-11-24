import os
import glob
import requests

API_URL = "https://ollama.com/api/chat"
HEADERS = {"Authorization": "Bearer " + os.environ["OLLAMA_API_KEY"]}

read_file_tool_schema = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Use this when the user wants to read a file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "the path of the file to read"},
            },
            "required": ["path"]
        }
    }
}

list_files_schema = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "Use this when the user wants to list files in a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "the path of the directory to list"}
            },
            "required": []
        }
    }
}


def agent(messages):
    tools = [
        read_file_tool_schema,
        list_files_schema
    ]

    payload = {
        "model": "gpt-oss:20b",
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


tool_called = True
messages = [
    {
        "role": "user",
        "content": """
        Review the legal citations in legal_memo.txt.

        First, read the memo file.
        Then, list and read the case files in case_1.txt, case_2.txt, case_3.txt.

        Compare every case citation in the memo against the actual case law.

        Check whether:
        1. The case citations are accurate.
        2. The cases support the legal rules stated in the memo.
        3. The descriptions of the case holdings are correct.
        4. The memo misquotes or misrepresents any case.
        5. Any legal statements lack support from the cases.
        Classify each citation as:
            ACCURATE
            PARTIALLY ACCURATE
            INACCURATE
            UNSUPPORTED
            UNABLE TO VERIFY

For each citation, explain what the memo claims,
what the actual opinion establishes, any discrepancies,
and how the memo should be corrected.

Conclude with an overall assessment of citation accuracy.

Use only the provided opinions. Do not invent facts,
holdings, quotations, or legal authority.

        Identify errors and explain how to correct them.
        Do not invent case law or citations.
        Provide a final citation review with your findings.
        """
    }
]

while tool_called:
    message = agent(messages)

    tool_called = "tool_calls" in message

    if tool_called:
        messages.append(message)

        tool_calls = message["tool_calls"]
        tool_call = tool_calls[0]

        function_name = tool_call["function"]["name"]
        function_arguments = tool_call["function"]["arguments"]

        if function_name == "list_files":
            path = "files"
     

            if "path" in function_arguments:
                path = function_arguments["path"]

            files = glob.glob(f"{path}/*")
            output = files

        if function_name == "read_file":
            path = function_arguments["path"]

            with open(path, "r") as file:
                file_content = file.read()

            output = file_content

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
        print(message["content"])
