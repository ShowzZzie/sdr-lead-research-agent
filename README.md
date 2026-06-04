# SDR Lead Research Agent

An AI-powered agent that researches B2B companies by domain and returns a structured lead profile for sales development workflows. It fetches a company homepage, detects common marketing/sales tech from HTML patterns, and uses Claude to synthesize company, contact, funding, fit, and news signals into a validated JSON schema.

## What it Does

Given a company domain (e.g. `monday.com`), the agent:

1. **Fetches the homepage** over HTTPS and extracts visible text for the model.
2. **Detects tech stack signals** by matching known vendor patterns in the raw HTML (e.g. HubSpot, Segment, Intercom).
3. **Runs a tool-calling loop** with Anthropic Claude until research is complete, then requests a final structured `LeadProfile` JSON object.
4. **Persists results** in a local SQLite database, including token usage and optional job linkage.

You can run research via the **CLI** (synchronous, prints or writes JSON) or the **HTTP API** (async jobs with status polling).

The output schema (`LeadProfile`) includes:

- **Company** — name, category, description, employee estimates, growth signals, sources
- **People** — contacts with roles (when inferred)
- **Tech signals** — tools detected or inferred, with confidence and sources
- **Funding events**, **fit signals**, and **news items** — each with provenance fields where applicable

## Architecture

<!-- Add your architecture notes here -->

## Setup

### Prerequisites

- Python **3.14+**
- [uv](https://docs.astral.sh/uv/) (recommended) or another environment manager
- An [Anthropic API key](https://console.anthropic.com/)

### Install

```bash
git clone <repository-url>
cd sdr_lead_research_agent
uv sync
```

### Environment variables

Copy the example env file and set your API key:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude |
| `LOG_LEVEL` | No | Logging level (default: `INFO`) |

The app loads `.env` on startup via `python-dotenv`. Without `ANTHROPIC_API_KEY`, the process exits at import time.

### Run tests (optional)

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

### Database

Profiles and jobs are stored in `database.db` (SQLite) in the project root. The file is created automatically on first run.

## Project Structure

```
sdr_lead_research_agent/
├── src/lra/
│   ├── agent.py              # Tool-calling loop and orchestration
│   ├── api.py                # FastAPI routes and background jobs
│   ├── cli.py                # Typer CLI (`lra` command)
│   ├── config.py             # Env, model, logging, DB path
│   ├── database.py           # SQLModel models and persistence
│   ├── llm.py                # Anthropic client wrapper
│   ├── schemas.py            # Pydantic models (LeadProfile, JobStatus, …)
│   └── tools/
│       ├── fetch_homepage.py # HTTP fetch + tool definition
│       └── extract_tech_stack.py  # HTML pattern matching + tool definition
├── tests/unit/               # API, database, and tool unit tests
├── pyproject.toml
├── uv.lock
├── .env.example
└── database.db               # Created at runtime (not committed)
```

## Known Limitations

- **Single-page research** — Only the company homepage is fetched; no crawling, LinkedIn, news APIs, or CRM integrations.
- **Truncated context** — Parsed homepage text sent to the model is capped at **3,000 characters**, so large or JS-heavy sites may lose detail.
- **Fixed tech patterns** — `extract_tech_stack` only recognizes a small hardcoded list of vendors in HTML; tools loaded dynamically or behind obfuscation are missed.
- **LLM-dependent fields** — Most profile fields (people, funding, fit signals, news) are inferred by the model from limited homepage context and may be incomplete, low-confidence, or incorrect without external verification.
- **No API authentication** — The FastAPI service has no auth; do not expose it publicly without a gateway.
- **In-process background jobs** — `BackgroundTasks` do not survive server restarts; there is no distributed queue or worker pool.
- **SQLite storage** — One local `database.db`; not suited for multi-instance deployments without replacing the persistence layer.
- **Profile lookup** — `GET /profiles/{domain}` returns only the **latest** profile for that domain; historical runs are stored but not exposed via API.
- **Failed job details** — `GET /research/{job_id}` returns status only; error messages from failed jobs are stored in the DB but not included in the response body.
- **Agent guardrails** — The tool loop stops after **15 iterations**; homepage fetch uses a **10s** HTTP timeout.
- **Runtime requirement** — Requires Python 3.14+ and a valid `ANTHROPIC_API_KEY` before any command or import of `lra.config`.
