# AI Job Recommender

**Resume analysis and job recommendations powered by AI.** Upload a PDF resume to receive an automated summary, skill-gap analysis, career roadmap, and curated job listings from LinkedIn and Naukri.

---

## Overview

This application helps candidates and recruiters quickly understand a resume and discover relevant opportunities. It uses **OpenAI (GPT-4o)** for resume analysis and **Apify** to fetch live job data from LinkedIn and Naukri. The project includes a **Streamlit web app** and an **MCP (Model Context Protocol) server** for integration with AI assistants and IDEs.

## Tech Stack

| Layer        | Technology |
|-------------|------------|
| **Language** | Python 3.13+ |
| **Web UI**  | Streamlit |
| **LLM**     | OpenAI API (GPT-4o) |
| **Job data**| Apify (LinkedIn, Naukri actors) |
| **PDF**     | PyMuPDF (fitz) |
| **Config**  | python-dotenv, env-based settings |
| **MCP**     | FastMCP |
| **Tests**   | pytest |
| **Deploy**  | Docker |

## Features

- **Resume summary** – Concise overview of skills, education, and experience.
- **Skill-gap analysis** – Identifies missing skills and certifications for stronger candidacy.
- **Career roadmap** – Actionable suggestions for learning and growth.
- **Job recommendations** – Fetches roles from LinkedIn and Naukri based on resume-derived keywords.
- **MCP integration** – Tools `fetchlinkedin` and `fetchnaukri` for use in Cursor and other MCP clients.
- **Production-oriented** – Input validation, error handling, retries, timeouts, safe HTML, and configurable limits.

## Design Highlights

- **Separation of concerns** – Config, PDF/LLM helpers, and job API are isolated in `src/`; app and MCP are thin entrypoints.
- **Security** – No `unsafe_allow_html` with raw user/LLM content; output is escaped. API keys via environment only.
- **Resilience** – Retries and timeouts for OpenAI and Apify; clear user-facing errors.
- **Operability** – Structured logging, env-based configuration, Docker and health check, documented config table.

## Requirements

- Python **3.13+**
- [OpenAI API key](https://platform.openai.com/api-keys)
- [Apify API token](https://console.apify.com/account/integrations)

## Quick Start

```bash
cd job
cp .env   # Add OPENAI_API_KEY and APIFY_API_TOKEN
pip install -r requirements.txt
streamlit run app.py
```

Open **http://localhost:8501** and upload a PDF resume.

## Setup

1. **Clone and enter the project**
   ```bash
   cd job
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   # or as editable package:
   pip install -e .
   # or with uv:
   uv sync
   ```

3. **Environment**
   ```bash
   cp  .env
   ```
   Edit `.env` and set:
   - `OPENAI_API_KEY` – [OpenAI API keys](https://platform.openai.com/api-keys)
   - `APIFY_API_TOKEN` – [Apify integrations](https://console.apify.com/account/integrations)

## Running the Application

### Streamlit (Web UI)

From the project root:

```bash
streamlit run app.py
```

Default URL: **http://localhost:8501**

### MCP Server (stdio)

```bash
python mcp_server.py
```

Configure your client to run this command. Available tools:

- **fetchlinkedin** – Fetch LinkedIn jobs by comma-separated keywords.
- **fetchnaukri** – Fetch Naukri jobs by comma-separated keywords.

## Project Structure

```
job/
├── app.py                 # Streamlit entrypoint
├── mcp_server.py          # MCP server entrypoint
├── src/
│   ├── config.py          # Environment and configuration
│   ├── helper.py          # PDF extraction, OpenAI client, safe HTML
│   └── job_api.py         # LinkedIn & Naukri via Apify
├── docs/
│   └── ARCHITECTURE.md    # Design and data flow
├── tests/
│   ├── conftest.py        # Pytest fixtures and env
│   ├── test_helper.py     # PDF and helper tests
│   ├── test_config.py     # Config tests
│   └── test_job_api.py    # Job API tests (mocked)
├── .env.example
├── Dockerfile
├── LICENSE
├── pyproject.toml
├── requirements.txt
└── README.md
```

For design and data flow, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Configuration

All configuration is via environment variables. Copy `.env.example` to `.env` and adjust as needed.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | OpenAI API key |
| `APIFY_API_TOKEN` | Yes | — | Apify API token |
| `OPENAI_MODEL` | No | `gpt-4o` | OpenAI model name |
| `OPENAI_TIMEOUT_SEC` | No | `60` | Request timeout (seconds) |
| `OPENAI_MAX_RETRIES` | No | `3` | Retries on failure |
| `APIFY_TIMEOUT_SEC` | No | `120` | Apify actor timeout (seconds) |
| `APIFY_MAX_RETRIES` | No | `2` | Retries for job fetch |
| `MAX_PDF_SIZE_MB` | No | `10` | Max resume upload size (MB) |
| `MAX_RESUME_CHARS` | No | `50000` | Max characters processed (truncated if longer) |
| `DEFAULT_JOB_ROWS` | No | `60` | Max jobs per source |
| `DEFAULT_LOCATION` | No | `india` | Default job search location |
| `LOG_LEVEL` | No | `INFO` | Logging level |

## Docker

```bash
docker build -t job-recommender .
docker run -p 8501:8501 --env-file .env job-recommender
```

For production, run behind a reverse proxy with HTTPS and restrict access as needed.

## Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

Tests use mocked external APIs. Ensure `OPENAI_API_KEY` and `APIFY_API_TOKEN` are set (e.g. in `.env`) so config loads.

## License

MIT License. See [LICENSE](LICENSE) for details.

