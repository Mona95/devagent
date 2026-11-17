import json
import os

from dotenv import load_dotenv
from groq import Groq

from agent.prompts import AGENT_SYSTEM_PROMPT
from agent.tools.analyze_code import analyze_code
from agent.tools.github_tool import github_repo
from agent.tools.read_url import read_url
from agent.tools.run_python import run_python
from agent.tools.web_search import web_search

load_dotenv()

# Tool registry: name -> function
TOOLS = {
    "web_search": web_search,
    "read_url": read_url,
    "run_python": run_python,
    "github_repo": github_repo,
    "analyze_code": analyze_code,
}

# Tool schemas: what the model sees.
# Parameter names must match the Python function arguments exactly.
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the internet for current information. Returns top results with titles, snippets and links.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_url",
            "description": "Fetch a webpage and return its readable text (truncated to 3000 characters).",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Full URL starting with http(s)://"}
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Execute Python code and return stdout/stderr. Use print() to see values. 10 second timeout.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Complete Python code to run"}
                },
                "required": ["code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "github_repo",
            "description": "Fetch info about a GitHub repository: description, stats, README and root files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "repo": {"type": "string", "description": 'Repository as "owner/repo" or a GitHub URL'}
                },
                "required": ["repo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_code",
            "description": "Analyze a piece of code for security issues, performance problems, bugs or general quality.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "The code to analyze"},
                    "analysis_type": {
                        "type": "string",
                        "enum": ["security", "performance", "bugs", "review", "general"],
                        "description": "What kind of analysis to run",
                    },
                },
                "required": ["code"],
            },
        },
    },
]


class DevAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "openai/gpt-oss-120b"
        self.max_iterations = 10

    def execute_tool(self, name: str, raw_arguments: str) -> str:
        """Run one tool call. Never raises: errors go back to the model as text."""
        if name not in TOOLS:
            return f"Error: unknown tool '{name}'"
        try:
            arguments = json.loads(raw_arguments or "{}")
            return TOOLS[name](**arguments)
        except json.JSONDecodeError:
            return "Error: tool arguments were not valid JSON"
        except TypeError as e:
            return f"Error: invalid arguments for {name}: {e}"
        except Exception as e:
            return f"Error while running {name}: {e}"

    def run(self, task: str, stream_callback=None, should_cancel=None):
        def emit(event: dict):
            if stream_callback:
                stream_callback(event)

        def cancelled() -> bool:
            return bool(should_cancel and should_cancel())

        cancelled_result = {
            "success": False,
            "steps": [],
            "answer": "Cancelled by user.",
        }

        messages = [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": task},
        ]
        steps = []

        for _ in range(self.max_iterations):
            if cancelled():
                print("[agent] cancelled, stopping")
                return cancelled_result

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                max_tokens=2000,
                temperature=0.1,
            )
            message = response.choices[0].message

            # No tool calls: the model is giving its final answer
            if not message.tool_calls:
                final = {"type": "final", "content": message.content or ""}
                steps.append(final)
                emit(final)
                return {"success": True, "steps": steps, "answer": final["content"]}

            # Any text alongside tool calls is the agent's reasoning
            if message.content:
                emit({"type": "thought", "content": message.content})

            # Add the assistant's tool request to history
            messages.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in message.tool_calls
                ],
            })

            # Run each requested tool and add its result to history
            for call in message.tool_calls:
                if cancelled():
                    print("[agent] cancelled, stopping")
                    return cancelled_result

                name = call.function.name
                raw_args = call.function.arguments

                call_step = {"type": "tool_call", "tool": name, "input": raw_args}
                steps.append(call_step)
                emit(call_step)

                result = self.execute_tool(name, raw_args)

                result_step = {"type": "tool_result", "tool": name, "result": result[:500]}
                steps.append(result_step)
                emit(result_step)

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result,
                })

        failure = {
            "type": "error",
            "content": "Agent could not complete the task within the iteration limit.",
        }
        steps.append(failure)
        emit(failure)
        return {"success": False, "steps": steps, "answer": failure["content"]}