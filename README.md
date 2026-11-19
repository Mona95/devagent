# DevAgent: Multi-Tool Autonomous AI Agent

DevAgent is an AI agent that decides for itself which tools to use, and in what order, to complete developer tasks. You give it a task, and you watch it think, call tools and answer, step by step.

The agent loop is built from scratch on top of the Groq API, with no agent framework.

---

## What it does

Example tasks:

- "Use Python to calculate the 20th Fibonacci number"
- "Look at the GitHub repo tiangolo/fastapi and summarize what it does"
- "Search the web for the latest stable Python version, then write and run code that prints it"

The agent picks the tools, chains them, reads the results and decides when it is done. Nothing about the sequence is hardcoded.

## Tools

| Tool | What it does |
|------|--------------|
| `web_search` | Searches the web via SerpAPI |
| `read_url` | Fetches a webpage and extracts readable text |
| `run_python` | Executes Python code in a subprocess with a timeout |
| `github_repo` | Fetches repo stats, README and root files |
| `analyze_code` | Reviews code for security, performance or bugs |

---

## How it works

```
User task
   ↓
Agent loop:
  1. Send history + tool schemas to the LLM
  2. LLM answers with a final reply, or with tool calls
  3. Run the requested tools
  4. Append the results to the history
  5. Repeat until there are no more tool calls (or the iteration limit is hit)
   ↓
Final answer, streamed to the UI step by step
```

Key design decisions:

- **Native tool calling.** Tools are described with JSON schemas and the model returns structured `tool_calls`. An earlier version parsed a text format with regex, which was fragile.
- **Conversation history is the agent's memory.** The LLM is stateless, so the full history is resent on every iteration.
- **Streaming with Server-Sent Events.** Each step is pushed to the browser as it happens. A worker thread produces events into a queue and the response generator consumes them.
- **Cooperative cancellation.** The Stop button aborts the request in the browser. The server detects the disconnect and sets a flag, and the agent stops between steps so it does not keep spending tokens.
- **Errors are data.** Tool failures are returned to the model as text, so it can retry differently instead of crashing.
- **Bounded cost.** Tool outputs are truncated and the number of iterations is capped.

---

## Tech stack

**Backend:** Python, FastAPI, Groq (`openai/gpt-oss-120b`), SerpAPI, BeautifulSoup, httpx

**Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, react-markdown

---

## Running locally

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Groq API key (free at console.groq.com)
- A SerpAPI key (free tier: 100 searches/month)
- A GitHub token (optional, raises API rate limits)

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Fill in GROQ_API_KEY, SERPAPI_KEY, GITHUB_TOKEN

make run
# → http://localhost:3002  (API docs at /docs)
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## Project structure

```
devagent/
├── backend/
│   ├── agent/
│   │   ├── agent.py        # Agent loop, tool schemas, cancellation
│   │   ├── prompts.py      # System prompt
│   │   └── tools/          # One file per tool
│   └── main.py             # FastAPI app, SSE streaming endpoint
└── frontend/
    └── src/
        ├── api/            # Streaming fetch client
        ├── components/     # TurnView, EventStep, TaskInput
        ├── hooks/          # useAgent (stream state, abort)
        └── types/          # AgentEvent discriminated union
```

---

## Security

`run_python` executes code written by the model on the machine running the backend. This is fine for local use, but **do not expose this backend publicly as it is**. Anyone who can reach it could run code on your server and read its environment variables. A public deployment needs a sandbox (a container with no network and no secrets, or a service like E2B) or the tool removed.

Model output is treated as untrusted. Answers are rendered with `react-markdown`, which does not render raw HTML.

## Known limitations

- Each task is independent: the agent does not remember previous tasks
- No authentication or rate limiting
- Cancellation takes effect between steps, so a step already in progress still finishes
- Tool outputs are truncated, so long pages may lose information

## Planned improvements

- [ ] Sandboxed code execution
- [ ] Multi-turn conversations
- [ ] Conversation history saved to a database
- [ ] Authentication and per-user rate limits
- [ ] Deployment with the code execution tool disabled or sandboxed

---

## Author

Built by [Mona](https://github.com/Mona95) as part of an AI engineering portfolio.