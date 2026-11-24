import os
import glob
import json
import requests

API_URL = "https://ollama.com/api/chat"

HEADERS = {"Authorization": "Bearer " + os.environ["OLLAMA_API_KEY"]}

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

read_file_tool_schema = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a text file, including a legal memo or case opinion.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path of the file to read."
                }
            },
            "required": ["path"]
        }
    }
}

list_files_schema = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "List files in a directory. Use this to locate the legal memo and case opinions.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The directory to search."
                }
            },
            "required": ["path"]
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
        timeout=300
    )

    response.raise_for_status()
    data = response.json()
    message = data["message"]
    return message

def get_safe_path(path):

    if os.path.isabs(path):
        full_path = os.path.abspath(path)
    else:
        full_path = os.path.abspath(
            os.path.join(PROJECT_DIR, path)
        )

    if os.path.commonpath(
        [PROJECT_DIR, full_path]
    ) != PROJECT_DIR:
        raise ValueError("Path is outside the project directory.")

    return full_path

def list_files(path="."):

    full_path = get_safe_path(path)

    if not os.path.isdir(full_path):
        return "Directory not found: " + path

    files = glob.glob(
        os.path.join(full_path, "*")
    )

    output = []

    for file in sorted(files):

        relative_path = os.path.relpath(
            file, PROJECT_DIR
        )

        if os.path.isdir(file):
            output.append("[FOLDER] " + relative_path)

        else:
            output.append("[FILE] " + relative_path)

    if not output:
        return "No files found in this directory."

    return "\n".join(output)

def read_file(path):

    full_path = get_safe_path(path)

    if not os.path.isfile(full_path):
        return "File not found: " + path

    if os.path.getsize(full_path) > 2000000:
        return "File is too large to read."

    try:
        with open(
            full_path,
            "r",
            encoding="utf-8",
            errors="replace"
        ) as file:

            file_content = file.read()

        return file_content

    except Exception as error:

        return "Error reading file: " + str(error)

messages = [
    {
        "role": "user",
        "content": """
Review the legal memorandum in the memo folder against
the judicial opinions in the cases folder.

Find and read the documents using the available tools.
Identify every case citation in the memo and determine
whether the memo accurately represents the cited case's
facts, holding, reasoning, and limitations.

Classify each citation as:
- ACCURATE
- PARTIALLY ACCURATE
- INACCURATE
- UNSUPPORTED
- UNABLE TO VERIFY

For each citation, explain what the memo claims,
what the actual opinion establishes, any discrepancies,
and how the memo should be corrected.

Conclude with an overall assessment of citation accuracy.

Use only the provided opinions. Do not invent facts,
holdings, quotations, or legal authority.
"""
    }
]

tool_called = True
iteration = 0
while tool_called and iteration < 30:
    iteration += 1
    message = agent(messages)
    tool_called = "tool_calls" in message

    if tool_called:
        print("\nAI is accessing project files...\n")
        messages.append(message)
        tool_calls = message["tool_calls"]

        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            function_arguments = tool_call["function"]["arguments"]

            if isinstance(function_arguments, str):
                function_arguments = json.loads(
                    function_arguments
                )

            try:

                if function_name == "list_files":

                    path = function_arguments.get(
                        "path", "."
                    )

                    print(
                        "Listing files in:", path
                    )

                    output = list_files(path)

                elif function_name == "read_file":

                    path = function_arguments["path"]

                    print(
                        "Reading file:", path
                    )

                    output = read_file(path)

                else:

                    output = "Unknown tool: " + function_name

            except Exception as error:

                output = "Tool error: " + str(error)

            tool_message = {
                "role": "tool",
                "tool_name": function_name,
                "content": str(output)
            }

            messages.append(tool_message)

    else:

        print("\n" + "=" * 60)

        print("LEGAL MEMORANDUM CITATION ACCURACY REVIEW")

        print("=" * 60 + "\n")

        final_report = message.get("content", "")

        print(final_report)

        report_path = os.path.join(
            PROJECT_DIR,
            "citation_review_report.txt"
        )

        with open(
            report_path,
            "w",
            encoding="utf-8"
        ) as report_file:

            report_file.write(final_report)

        print("\n" + "=" * 60)

        print("Review saved to citation_review_report.txt")

        print("=" * 60)


if tool_called:

    print(
        "The review stopped after reaching the maximum "
        "number of tool-calling rounds."
    )
