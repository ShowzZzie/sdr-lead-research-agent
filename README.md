# SDR Lead Research Agent

An AI-powered agent that researches B2B companies by domain and returns a structured lead profile for sales development workflows. It fetches a company homepage, detects common marketing/sales tech from HTML patterns, uses Anthropic web search for external signals, and synthesizes company, contact, funding, fit, and news data into a validated JSON schema via Claude.

## What it Does

Given a company domain (e.g. `monday.com`), the agent:

1. **Fetches the homepage** over HTTPS and extracts visible text for the model.
2. **Detects tech stack signals** by matching known vendor patterns in the raw HTML (e.g. HubSpot, Segment, Intercom).
3. **Searches the web** via Anthropic's built-in `web_search` tool (limited to one search per run) for news, funding, and leadership information not on the homepage.
4. **Runs a tool-calling loop** with Claude Sonnet 4.6 until research is complete, then requests a final structured `LeadProfile` JSON object.
5. **Persists results** in a local SQLite database, including token usage and optional job linkage.

You can run research via the **CLI** (prints or writes JSON), the **HTTP API** (async jobs with status polling), or **MCP** (expose `research_company` to MCP-compatible clients such as Cursor).

The output schema (`LeadProfile`) includes:

- **Company** — name, category, description, employee estimates, growth signals, sources
- **People** — contacts with roles (when inferred)
- **Tech signals** — tools detected or inferred, with confidence and sources
- **Funding events**, **fit signals**, and **news items** — each with provenance fields where applicable

## Architecture

The whole system is based on an agentic loop utilizing Claude Sonnet 4.6. After the user submits a domain, the CLI, API, or MCP server passes it to the Agent module, where the loop starts. An initial prompt is sent to Claude, who requests tools from the Tools package (executed in Python) and Anthropic's server-side `web_search` tool. If the model stops with `tool_use`, the loop continues until `end_turn`. On `end_turn`, the agent makes a final call to return a JSON `LeadProfile`. The stack is fully async (`AsyncAnthropic`, `httpx.AsyncClient`) end to end.

### The distinction between LLM.py and Agent.py

LLM and Agent are separate modules for modularity. To swap models or providers, change Config and LLM and leave Agent.py mostly untouched. Agent.py is the only module that knows the user's domain — LLM is blind to user input and only passes data to and from the model.

### Why Tools is a package

Splitting tools into separate modules within a single package gives individual units for testing and makes it easy to add or remove tools (one file = one tool). Custom tools (`fetch_homepage`, `extract_tech_stack`) live here; `web_search` is an Anthropic server tool configured in Agent.py, not in the Tools package.

### How the API wraps the Agent

API.py calls Agent.py's async `main()` via a helper function. That helper ensures the database exists, schedules `main()` as a background task, and updates job statuses so jobs do not stay on `pending` forever.

### MCP server

`mcp_server.py` is a thin FastMCP wrapper that exposes a single `research_company(domain)` tool. It calls the same `main()` used by the CLI and API and returns the profile as JSON.

To connect to Claude Desktop, add the following to
`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sdr-lead-research-agent": {
      "command": "/absolute/path/to/.venv/bin/lra-mcp"
    }
  }
}
```

The server uses your own `ANTHROPIC_API_KEY` from `.env` — each user must
provide their own key and pays for their own API usage.

## Setup

### Prerequisites

- Python **3.14+**
- [uv](https://docs.astral.sh/uv/) (recommended) or another environment manager
- An [Anthropic API key](https://console.anthropic.com/)

### Install

```bash
git clone <repository-url>
cd sdr_lead_research_agent
uv sync --group dev
```

`uv sync` installs the package in editable mode (`[tool.uv] package = true` in `pyproject.toml`).

### Environment variables

Copy the example env file and set your API key:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude |

The app loads `.env` on startup via `python-dotenv`. Without `ANTHROPIC_API_KEY`, the process exits at import time.

### Run tests (optional)

Unit tests (no live API calls):

```bash
uv run pytest tests/unit/ -v
```

Eval tests (schema validation, golden-profile checks, LLM-as-judge — require `ANTHROPIC_API_KEY` and cached or live agent runs):

```bash
uv run pytest tests/evals/ -v
```

Run everything:

```bash
uv run pytest tests/ -v
```

## Usage

### CLI

Research a domain and print JSON to stdout:

```bash
uv run lra research --domain monday.com
```

Write results to a file:

```bash
uv run lra research --domain monday.com --output lead-profile.json
```

You can also invoke the agent module directly:

```bash
uv run python -m lra.agent
```

(Default domain in `__main__` is `monday.com`.)

### HTTP API

Start the server:

```bash
uv run uvicorn lra.api:app --reload
```

**Create a research job** (runs in the background):

```bash
curl -X POST http://127.0.0.1:8000/research \
  -H "Content-Type: application/json" \
  -d '{"domain": "monday.com"}'
```

Example response:

```json
{"message": "job_created", "job_id": 1, "status": "pending"}
```

**Poll job status** (includes profile when `completed`):

```bash
curl http://127.0.0.1:8000/research/1
```

**Fetch the latest stored profile for a domain**:

```bash
curl http://127.0.0.1:8000/profiles/monday.com
```

Job statuses: `pending` → `running` → `completed` or `failed`.

### MCP

Start the MCP server:

```bash
uv run lra-mcp
```

This exposes a `research_company(domain)` tool that returns a structured JSON profile. Wire it into your MCP client configuration (e.g. Cursor) to call research from the IDE.

### Database

Profiles and jobs are stored in `database.db` (SQLite) in the project root. The file is created automatically on first run.

## Project Structure

```
sdr_lead_research_agent/
├── src/lra/
│   ├── agent.py              # Async tool-calling loop and orchestration
│   ├── api.py                # FastAPI routes and background jobs
│   ├── cli.py                # Typer CLI (`lra` command)
│   ├── config.py             # Env, model, logging, DB path
│   ├── database.py           # SQLModel models and persistence
│   ├── llm.py                # Async Anthropic client wrapper
│   ├── mcp_server.py         # FastMCP server (`lra-mcp` command)
│   ├── schemas.py            # Pydantic models (LeadProfile, JobStatus, …)
│   └── tools/
│       ├── fetch_homepage.py # Async HTTP fetch + tool definition
│       └── extract_tech_stack.py  # HTML pattern matching + tool definition
├── tests/
│   ├── unit/                 # API, database, and tool unit tests
│   └── evals/                # Schema, golden-profile, and LLM-judge evals
├── pyproject.toml
├── uv.lock
├── .env.example
└── database.db               # Created at runtime (not committed)
```

## Known Limitations

- **Limited external research** — Homepage fetch plus one web search per run; no crawling, LinkedIn, dedicated news APIs, or CRM integrations.
- **Web search cap** — Anthropic `web_search` is limited to **1 use** per run (`max_uses: 1`).
- **Truncated context** — Parsed homepage text sent to the model is capped at **3,000 characters**, so large or JS-heavy sites may lose detail.
- **Fixed tech patterns** — `extract_tech_stack` only recognizes a small hardcoded list of vendors in HTML; tools loaded dynamically or behind obfuscation are missed.
- **LLM-dependent fields** — People, funding, fit signals, and news may still be incomplete or incorrect even with web search; verify critical fields before outreach.
- **Sequential tool dispatch** — Custom tools in the same iteration are not run in parallel yet (`fetch_homepage` and `extract_tech_stack` typically run in separate iterations).
- **No API authentication** — The FastAPI service has no auth; do not expose it publicly without a gateway.
- **In-process background jobs** — `BackgroundTasks` do not survive server restarts; there is no distributed queue or worker pool.
- **SQLite storage** — One local `database.db`; not suited for multi-instance deployments without replacing the persistence layer.
- **Profile lookup** — `GET /profiles/{domain}` returns only the **latest** profile for that domain; historical runs are stored but not exposed via API.
- **Failed job details** — `GET /research/{job_id}` returns status only; error messages from failed jobs are stored in the DB but not included in the response body.
- **Agent guardrails** — The tool loop stops after **15 iterations**; homepage fetch uses a **10s** HTTP timeout.
- **Runtime requirement** — Requires Python 3.14+ and a valid `ANTHROPIC_API_KEY` before any command or import of `lra.config`.
