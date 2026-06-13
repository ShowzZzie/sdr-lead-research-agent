# SDR Lead Research Agent

An AI agent that researches B2B companies by domain and returns structured lead profiles. Given a domain, it fetches the homepage, extracts tech stack signals from HTML, searches the web for current news and funding data, and synthesizes everything into a validated JSON schema via Claude Sonnet 4.6.

Callable via CLI, REST API, or directly from Claude Desktop via MCP.

---

## What it Produces

Simplified shape of the `LeadProfile` schema (see `src/lra/schemas.py` for full field names and types):

```json
{
  "company": { "name", "website", "category", "description", "employees_amount", "yoy_growth", "stock_symbol", "sources" },
  "person": [{ "name", "role", "email", "source" }],
  "tech_signal": [{ "tool", "confidence", "source" }],
  "funding_events": [{ "round", "date", "amount_raised", "investors", "source" }],
  "fit_signal": [{ "reason", "confidence", "source" }],
  "news_items": [{ "text", "date_created", "source" }]
}
```

Key claims include a `source` (URL, name, retrieval date) where available.

---

## Architecture

The agent runs a tool-calling loop with Claude Sonnet 4.6. Each iteration either executes a tool or produces a final structured response.

**Tools:**
- `fetch_homepage` — async HTTP fetch via `httpx.AsyncClient`
- `extract_tech_stack` — pattern matching against known vendor signatures in raw HTML
- `web_search` — Anthropic server-side tool; no Python implementation required

**Loop flow:**
1. Initial prompt sent to Claude with all three tools available
2. Claude requests tools (`stop_reason: tool_use`) → Python executes them → results appended to messages
3. Claude searches the web autonomously via `web_search` (server-side, within the same turn)
4. On `end_turn`, a final synthesis call extracts a structured `LeadProfile` from the conversation
5. Profile stored in SQLite, token costs logged to Langfuse

**Stack:** Python 3.14, `uv`, `AsyncAnthropic`, `httpx.AsyncClient`, FastAPI, SQLModel, Typer, FastMCP, Langfuse, Pydantic v2

**Separation of concerns:**
- `llm.py` — provider-agnostic async client wrapper; swap model/provider here without touching agent logic
- `agent.py` — loop logic, tool dispatch, prompt construction; only file that knows the domain
- `tools/` — one file per tool, each independently testable
- `mcp_server.py` — thin FastMCP wrapper exposing `research_company(domain)` to MCP clients

---

## Evals

Three-layer evaluation harness:

| Layer | What it tests | Cost |
|-------|--------------|------|
| Schema | Pydantic validation on valid and malformed inputs | $0 |
| Ground truth | 13 golden company profiles with assertable facts | $0 (cached) |
| LLM-as-judge | Claude Opus 4.7 scores fit signals, descriptions, and tech signal confidence against a rubric | ~$0.01/run |

38 tests total. MyPy strict mode and Ruff are configured in `pyproject.toml`.

---

## Tests

**Unit tests** — API, database, and tools; no live Anthropic calls:

```bash
uv run pytest tests/unit/ -v
```

**Eval tests** — schema validation, 13 golden-profile ground-truth checks, and LLM-as-judge (Opus 4.7). Ground-truth evals use cached profiles in `database.db` when available; LLM-judge tests require prior runs and an `ANTHROPIC_API_KEY`:

```bash
uv run pytest tests/evals/ -v
```

**Everything:**

```bash
uv run pytest tests/ -v
```

Ground-truth evals hit the live agent on cache miss. Run research on golden domains first, or expect API cost on first pass.

---

## Setup

### Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- [Anthropic API key](https://console.anthropic.com/)

### Install

```bash
git clone https://github.com/ShowzZzie/sdr-lead-research-agent
cd sdr_lead_research_agent
uv sync --group dev
```

`uv sync` installs the package in editable mode (`[tool.uv] package = true` in `pyproject.toml`).

### Environment

```bash
cp .env.example .env
# Add your ANTHROPIC_API_KEY
```

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | Anthropic API key for Claude |

The app loads `.env` on startup via `python-dotenv`. Without `ANTHROPIC_API_KEY`, the process exits at import time.

Optionally add Langfuse keys for observability:

```
LANGFUSE_SECRET_KEY=...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

Without Langfuse keys, tracing is disabled silently (no-op client).

---

## Usage

### CLI

```bash
# Fresh research
uv run lra research --domain rippling.com

# Use cached profile (no API call)
uv run lra research --domain rippling.com --use-cache

# Write to file
uv run lra research --domain rippling.com --output rippling.json
```

### HTTP API

```bash
uv run uvicorn lra.api:app --reload
```

**Single domain:**

```bash
curl -X POST http://127.0.0.1:8000/research \
  -H "Content-Type: application/json" \
  -d '{"domain": "rippling.com"}'
# → {"message": "job_created", "job_id": 1, "status": "pending"}

curl http://127.0.0.1:8000/research/1
# → {"status": "completed", "profile": {...}}
```

**Batch (bounded by `asyncio.Semaphore(3)`):**

```bash
curl -X POST http://127.0.0.1:8000/research/batch \
  -H "Content-Type: application/json" \
  -d '{"domains": ["stripe.com", "hubspot.com", "linear.app"]}'
# → {"jobs": [{"domain": ..., "job_id": ..., "status": "pending"}, ...]}
```

**Fetch cached profile:**

```bash
curl http://127.0.0.1:8000/profiles/rippling.com
```

Job statuses: `pending` → `running` → `completed` or `failed`.

### MCP (Claude Desktop)

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sdr-lead-research-agent": {
      "command": "/absolute/path/to/.venv/bin/lra-mcp"
    }
  }
}
```

Restart Claude Desktop. Then in any conversation: `research rippling.com`

You can also run the server standalone for Cursor or other MCP clients:

```bash
uv run lra-mcp
```

> The MCP server uses your own `ANTHROPIC_API_KEY` — each user pays for their own API usage.

---

## Project Structure

```
sdr_lead_research_agent/
├── src/lra/
│   ├── agent.py              # Async tool-calling loop
│   ├── api.py                # FastAPI: single + batch endpoints, job queue
│   ├── cli.py                # Typer CLI (lra research)
│   ├── config.py             # Env, model config, logging, DB path
│   ├── database.py           # SQLModel: Job + Profile tables
│   ├── llm.py                # AsyncAnthropic wrapper (call + final)
│   ├── mcp_server.py         # FastMCP server (lra-mcp)
│   ├── schemas.py            # Pydantic: LeadProfile, Company, Person, …
│   └── tools/
│       ├── fetch_homepage.py
│       └── extract_tech_stack.py
├── tests/
│   ├── unit/                 # API, database, tool tests (no API calls)
│   └── evals/
│       ├── golden_profiles.py
│       ├── rubric.py
│       ├── test_schema_evals.py
│       ├── test_ground_truth_evals.py
│       └── test_llm_judge_evals.py
├── pyproject.toml
├── uv.lock
├── .env.example
└── database.db               # Created at runtime, not committed
```

---

## Known Limitations

- **Local-first, not hosted** — Designed for CLI, MCP, and local API use. No auth, rate limits, or production hardening unless you add them.
- **One web search per run** — `max_uses: 1` on Anthropic `web_search`; increase in `agent.py` for richer profiles at higher cost.
- **3,000 char homepage truncation** — Parsed homepage text sent to the model is capped; JS-heavy or large sites lose detail.
- **Fixed tech patterns** — `extract_tech_stack` matches a hardcoded vendor list; obfuscated or dynamically loaded tools are missed.
- **LLM-dependent fields** — People, funding, fit signals, and news may be incomplete or wrong even with web search; verify before outreach.
- **No crawling or CRM integrations** — Homepage fetch plus one web search only; no LinkedIn, news APIs, or enrichment pipelines.
- **No API auth** — Do not expose the FastAPI server publicly without a gateway; anyone who can reach it can spend your Anthropic credits.
- **In-process background jobs** — `BackgroundTasks` and batch `asyncio.create_task` do not survive server restarts; no distributed queue.
- **SQLite only** — Single local `database.db`; not suited for multi-instance deployments.
- **Profile lookup** — `GET /profiles/{domain}` returns only the latest profile; older runs are stored but not exposed.
- **Failed job details** — `GET /research/{job_id}` returns status only; error messages are stored in the DB but not in the response body.
- **Agent guardrails** — Tool loop stops after 15 iterations; homepage fetch uses a 10s HTTP timeout.
- **Sequential tool dispatch** — `fetch_homepage` and `extract_tech_stack` typically run in separate loop iterations; parallel dispatch is deferred (TODO in `agent.py`).
