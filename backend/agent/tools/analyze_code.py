import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def analyze_code(code: str, analysis_type: str = "general") -> str:
    """
    Analyze code using Groq LLM.
    analysis_type options: security, performance, bugs, general, review
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompts = {
        "security": "Analyze this code for security vulnerabilities. Be specific about line numbers and severity.",
        "performance": "Analyze this code for performance issues and optimization opportunities.",
        "bugs": "Find potential bugs, edge cases, and logical errors in this code.",
        "review": "Do a thorough code review covering style, structure, best practices, and potential issues.",
        "general": "Analyze this code and provide insights about its quality, structure, and any issues."
    }

    prompt = prompts.get(analysis_type, prompts["general"])

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": f"{prompt}\n\nBe concise but thorough. Format your response with clear sections."
            },
            {
                "role": "user",
                "content": f"```\n{code}\n```"
            }
        ],
        max_tokens=1000
    )

    return response.choices[0].message.content