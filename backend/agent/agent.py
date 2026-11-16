import os
import re
from groq import Groq
from dotenv import load_dotenv
from agent.prompts import AGENT_SYSTEM_PROMPT
from agent.tools.web_search import web_search
from agent.tools.read_url import read_url
from agent.tools.run_python import run_python
from agent.tools.github_tool import github_repo
from agent.tools.analyze_code import analyze_code

load_dotenv()

# Tool registry — maps tool names to functions
TOOLS = {
    "web_search": web_search,
    "read_url": read_url,
    "run_python": run_python,
    "github_repo": github_repo,
    "analyze_code": analyze_code
}

class DevAgent:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "openai/gpt-oss-120b"
        self.max_iterations = 10

    def parse_response(self, response: str) -> dict:
        """
        Parse the agent's response to extract:
        - thought: the agent's reasoning
        - tool: which tool to call (if any)
        - input: the tool input
        - final_answer: the final response (if done)
        """
        result = {
            "thought": "",
            "tool": None,
            "input": None,
            "final_answer": None
        }

        # Extract THOUGHT
        thought_match = re.search(
            r"THOUGHT:\s*(.+?)(?=TOOL:|FINAL_ANSWER:|$)",
            response, re.DOTALL
        )
        if thought_match:
            result["thought"] = thought_match.group(1).strip()

        # Extract TOOL and INPUT
        tool_match = re.search(r"TOOL:\s*(\w+)", response)
        input_match = re.search(
            r"INPUT:\s*(.+?)(?=THOUGHT:|TOOL:|FINAL_ANSWER:|$)",
            response, re.DOTALL
        )
        if tool_match:
            result["tool"] = tool_match.group(1).strip()
        if input_match:
            result["input"] = input_match.group(1).strip()

        # Extract FINAL_ANSWER
        answer_match = re.search(
            r"FINAL_ANSWER:\s*(.+)$",
            response, re.DOTALL
        )
        if answer_match:
            result["final_answer"] = answer_match.group(1).strip()

        return result

    def run(self, task: str, stream_callback=None):
        """
        Run the agent loop until task is complete or max iterations reached.
        stream_callback: optional function called with each step for streaming
        """
        messages = [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT},
            {"role": "user", "content": task}
        ]

        steps = []

        for iteration in range(self.max_iterations):
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.1
            )

            agent_response = response.choices[0].message.content
            parsed = self.parse_response(agent_response)

            # Stream the thought
            if parsed["thought"] and stream_callback:
                stream_callback({
                    "type": "thought",
                    "content": parsed["thought"]
                })

            # If we have a final answer — we're done
            if parsed["final_answer"]:
                step = {
                    "type": "final",
                    "content": parsed["final_answer"]
                }
                steps.append(step)
                if stream_callback:
                    stream_callback(step)
                return {
                    "success": True,
                    "steps": steps,
                    "answer": parsed["final_answer"]
                }

            # If we have a tool call — execute it
            if parsed["tool"] and parsed["input"]:
                tool_name = parsed["tool"]
                tool_input = parsed["input"]

                step = {
                    "type": "tool_call",
                    "tool": tool_name,
                    "input": tool_input
                }
                steps.append(step)

                if stream_callback:
                    stream_callback(step)

                # Execute the tool
                if tool_name in TOOLS:
                    tool_result = TOOLS[tool_name](tool_input)
                else:
                    tool_result = f"Error: Unknown tool '{tool_name}'"

                step_result = {
                    "type": "tool_result",
                    "tool": tool_name,
                    "result": tool_result[:500]  # limit for display
                }
                steps.append(step_result)

                if stream_callback:
                    stream_callback(step_result)

                # Add to conversation history
                messages.append({
                    "role": "assistant",
                    "content": agent_response
                })
                messages.append({
                    "role": "user",
                    "content": f"Tool result for {tool_name}:\n{tool_result}"
                })

            else:
                # No tool and no final answer — something went wrong
                break

        return {
            "success": False,
            "steps": steps,
            "answer": "Agent could not complete the task within the iteration limit."
        }