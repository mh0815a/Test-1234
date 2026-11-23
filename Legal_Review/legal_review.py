import os
import glob
import requests
import json
import pprint

API_URL = "https://ollama.com/api/chat"
HEADERS = {"Authorization": "Bearer " + os.environ["OLLAMA_API_KEY"]}


read_file_tool_schema = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Use this when the user wants to read a legal memo or case file.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path of the file to read"
                },
            },
            "required": ["path"]
        }
    }
}


list_files_schema = {
    "type": "function",
    "function": {
        "name": "list_files",
        "description": "Use this when the user wants to list files in the current working directory or a named directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path of the directory containing the memo and case files."
                }
            },
            "required": []
        }
    }
}


compare_cases_tool_schema = {
    "type": "function",
    "function": {
        "name": "compare_cases",
        "description": "Compare the legal memo against all uploaded case files to check whether citations and legal rules are accurate and whether the memo correctly applies the cases.",
        "parameters": {
            "type": "object",
            "properties": {
                "memo": {
                    "type": "string",
                    "description": "The text of the legal memo."
                },
                "cases": {
                    "type": "string",
                    "description": "The text of all case files used in the memo."
                }
            },
            "required": ["memo", "cases"]
        }
    }
}


def agent(messages):
    tools = [
        read_file_tool_schema,
        list_files_schema,
        compare_cases_tool_schema
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


def compare_cases(memo, cases):
    messages = [
        {
            "role": "system",
            "content": """
            You are a legal citation and case law review agent.

            Your job is to review a legal memo against ALL provided case files.

            Carefully compare the memo with the actual case law.

            Check the following:

            1. CITATION ACCURACY
            - Check whether case names and citations are correct.
            - Identify incorrect reporter citations, years, court names,
              pincites, and quotations.
            - Identify citations that do not support the proposition
              for which they are being used.

            2. ACCURACY OF CASE LAW
            - Determine whether the memo accurately describes each case.
            - Check whether the stated legal rule matches the actual holding.
            - Identify incorrect interpretations of the court's reasoning.
            - Identify missing limitations, exceptions, or qualifications.

            3. APPLICATION OF CASE LAW
            - Determine whether the memo correctly applies the case
              to the facts and legal arguments.
            - Identify situations where the memo stretches a holding
              beyond what the court actually decided.
            - Identify cases that are distinguishable from the
              proposition or facts in the memo.
            - Identify important counterarguments or contrary authority
              contained in the provided cases.

            4. MISSING SUPPORT
            - Identify statements of law that need citations.
            - Identify arguments that are not supported by the cases.
            - Identify cases that appear relevant but are not discussed.

            5. ANSWER KEY
            Create an answer key identifying every citation reviewed.
            For each citation, provide:
            - The citation as it appears in the memo.
            - Whether it is correct.
            - What the actual case says.
            - Whether the memo accurately describes the case.
            - Whether the memo correctly applies the case.
            - Any necessary corrections.

            IMPORTANT:
            - Compare the memo against all provided cases together.
            - Do not review only one case at a time.
            - Do not assume that a citation is accurate simply because
              the case name appears correct.
            - Do not invent case holdings, quotations, or pincites.
            - If the provided materials do not establish an answer,
              identify what needs additional verification.
            - Distinguish between citation errors and errors in
              legal reasoning.
            - Provide specific examples from the memo.
            """
        },
        {
            "role": "user",
            "content": f"""
            Review this legal memo against all of the provided cases.

            LEGAL MEMO:
            {memo}

            CASE FILES:
            {cases}

            Compare the memo to the cases and produce a detailed
            citation review and answer key.
            """
        }
    ]

    return agent(messages)


tool_called = True

messages = [
    {
        "role": "user",
        "content": """
        Review the legal memo in the memo folder against all case files
        in the cases folder.

        First, list the files and read the memo and all case files.
        Then compare the memo against every case simultaneously.

        Identify incorrect citations, inaccurate descriptions of cases,
        incorrect applications of legal rules, and unsupported arguments.

        Finally, create an answer key listing all citations reviewed
        and explaining any necessary corrections.
        """
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

        if function_name == "list_files":

            path = "."

            if "path" in function_arguments:
                path = function_arguments["path"]

            print(f"arguments for list_files: {path}")

            files = glob.glob(f"{path}/*")

            output = "\n".join(files)

        if function_name == "read_file":

            path = function_arguments["path"]

            with open(path, "r", encoding="utf-8") as file:
                file_content = file.read()

            output = file_content

        if function_name == "compare_cases":

            memo = function_arguments["memo"]
            cases = function_arguments["cases"]

            print("Comparing legal memo against all case files...")

            comparison = compare_cases(memo, cases)

            output = comparison["content"]

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

printer = pprint.pprint

print(last_message)
