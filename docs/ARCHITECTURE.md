# Architecture

High-level design of the AI Job Recommender application.

## Components

```
┌─────────────────┐     ┌──────────────────────────────────────────────────┐
│   Streamlit     │     │                      src/                          │
│   app.py        │────▶│  config.py  →  helper.py  →  job_api.py            │
│   (Web UI)      │     │     │              │              │                 │
└─────────────────┘     │     │              │              │                 │
                        │     ▼              ▼              ▼                 │
┌─────────────────┐     │  .env      OpenAI  PDF    Apify (LinkedIn/Naukri)  │
│   MCP server     │────▶│                                                    │
│   mcp_server.py  │     └──────────────────────────────────────────────────┘
└─────────────────┘
```

- **app.py** – Streamlit UI: file upload, calls to helper and job_api, error handling, safe rendering.
- **mcp_server.py** – FastMCP server exposing `fetchlinkedin` and `fetchnaukri`; delegates to job_api.
- **config.py** – Loads `.env`, validates required keys, exposes constants (timeouts, limits, model).
- **helper.py** – PDF text extraction (PyMuPDF), OpenAI chat with retries/timeout, HTML escaping for safe output.
- **job_api.py** – Apify client; LinkedIn and Naukri actors with retries and timeout.

## Data flow

1. User uploads PDF → `extract_text_from_pdf()` (size and type validated) → raw text (truncated if over limit).
2. Text is sent to OpenAI for: summary, skill gaps, roadmap (each with retries and timeout).
3. Optional: user requests jobs → OpenAI suggests keywords → `fetch_linkedin_jobs()` and `fetch_naukri_jobs()` via Apify.
4. Results are escaped and rendered; no raw user/LLM content in HTML.

## Design decisions

- **Config at startup** – Required API keys are checked on import so failures are fast and explicit.
- **No persistence** – Resume text is not stored; privacy notice is shown in the UI.
- **Retries and timeouts** – All external calls (OpenAI, Apify) use configurable retries and timeouts to avoid hanging and to improve resilience.
- **Safe HTML** – All dynamic content (LLM output) is escaped before rendering to prevent XSS.
- **MCP** – Job fetch is reusable by AI tools (e.g. Cursor) without duplicating logic; sync Apify calls are offloaded with `asyncio.to_thread` so the MCP server stays responsive.
