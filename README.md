# AI Job Recommender with MCP Tools

### Streamlit resume coach that plans via an agent loop and fetches jobs through MCP/Apify.

[![GitHub](https://img.shields.io/badge/repo-Real-time-Job-recommendation-system---MC-181717?logo=github)](https://github.com/ArchanaChetan07/Real-time-Job-recommendation-system---MCP)
[![Language](https://img.shields.io/badge/language-Python-3572A5)](https://github.com/ArchanaChetan07/Real-time-Job-recommendation-system---MCP)
[![License](https://img.shields.io/badge/license-See%20repository-yellow)](https://github.com/ArchanaChetan07/Real-time-Job-recommendation-system---MCP)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)](https://github.com/ArchanaChetan07/Real-time-Job-recommendation-system---MCP/actions)

---

## Overview

Job seekers need resume understanding, skill-gap guidance, and live LinkedIn/Naukri listings without rebuilding scrapers for every AI tool.

Streamlit UI extracts PDF text (PyMuPDF), calls OpenAI for summary/gaps/roadmap, and uses Apify actors for jobs; FastMCP server exposes fetchlinkedin/fetchnaukri; src/agent implements planner/loop/HITL/tools with retries/timeouts and demo mode.

Documented architecture with production-minded config, tests, Docker, and MCP reuse for IDEs/agents.

This repository is maintained as **production-minded portfolio work**: clear architecture, automated checks where present, and metrics that are **traceable to committed artifacts** (never invented).

---

## Architecture

Streamlit uploads PDF â†’ helper extracts text â†’ OpenAI analyzes resume â†’ optional keywording â†’ job_api/Apify (also via MCP) â†’ escaped render; agent loop plans tool use with HITL/demo guards.

```mermaid
flowchart TB
  U[User PDF] --> ST[Streamlit app.py]
  ST --> H[helper.py PDF + OpenAI]
  ST --> J[job_api.py Apify]
  MCP[mcp_server.py FastMCP] --> J
  ST --> A[src/agent loop/planner/tools]
  A --> H
  A --> J
```

```mermaid
sequenceDiagram
  participant U as User/Client
  participant S as Service/Pipeline
  participant E as Eval/Tools
  U->>S: request / job
  S->>E: execute
  E-->>S: results
  S-->>U: report / response
```

---

## Results & repository facts

> Only values found in code, configs, tests, or generated reports are listed. Absence of a clinical/ML accuracy number means it was **not** published in-repo.

| Metric | Value | Source |
|---|---|---|
| Tracked repository files | **30** | `git tree` |
| Python modules | **19** | `git tree *.py` |
| Default OPENAI_MODEL | **gpt-4o** | `src/config.py` |
| Default MAX_AGENT_STEPS | **8** | `src/config.py` |
| Default MAX_PDF_SIZE_MB | **10** | `src/config.py` |
| Default MAX_RESUME_CHARS | **50000** | `src/config.py` |
| Default DEFAULT_JOB_ROWS | **60** | `src/config.py` |
| OPENAI_TIMEOUT_SEC default | **60** | `src/config.py` |
| APIFY_TIMEOUT_SEC default | **120** | `src/config.py` |
| Tracked files | **30** | `git tree` |
| Python modules | **19** | `git tree` |
| Test-related paths | **6** | `git tree` |
| CI workflows | **Yes** | `.github/workflows` |
| Docker present | **Yes** | `repo root` |

```mermaid
%%{init: {'theme':'base'}}%%
pie showData title Language composition (bytes)
    "Python" : 98
    "Dockerfile" : 2
```

---

## Key features

- Resume PDF upload with size/type validation
- LLM summary, skill gaps, learning roadmap
- LinkedIn + Naukri job fetch via Apify
- MCP server tools for external agents
- DEMO_MODE when keys missing
- HITL flag and bounded agent steps
- XSS-safe HTML escaping of LLM output

---

## Tech stack

| Layer | Technology |
|---|---|
| ui | Streamlit |
| llm | OpenAI |
| mcp | FastMCP |
| jobs | Apify (LinkedIn/Naukri actors) |
| pdf | PyMuPDF |
| containers | Docker |
| ci | GitHub Actions |

---

## Skills demonstrated

Python · S · t · r · e · a · m · CI/CD · testing · automation

Keyword surface: **Python · Python · machine-learning · CI/CD · testing · API · Docker · automation · data-science · software-engineering · system-design · observability · LLM · cloud**

---

## Project structure

```text
Real-time-Job-recommendation-system---MCP/
â”œâ”€â”€ app.py / mcp_server.py
â”œâ”€â”€ docs/ARCHITECTURE.md
â”œâ”€â”€ src/{config,helper,job_api,tracing}.py
â”œâ”€â”€ src/agent/{loop,planner,tools,hitl,types}.py
â”œâ”€â”€ tests/
â”œâ”€â”€ Dockerfile / requirements.txt / pyproject.toml / uv.lock
â””â”€â”€ .env.example
```

---

## Installation & usage

```bash
git clone https://github.com/ArchanaChetan07/Real-time-Job-recommendation-system---MCP.git
cd Real-time-Job-recommendation-system---MCP
pip install -r requirements.txt
cp .env.example .env  # set OPENAI_API_KEY + APIFY_API_TOKEN or DEMO_MODE=1
streamlit run app.py
python mcp_server.py
```

---

## How it works

Config loads env keys and enables DEMO_MODE if missing. The UI extracts resume text, calls OpenAI with retries, and optionally fetches jobs. MCP exposes the same fetch tools for Cursor/other clients. Architecture.md details data flow and safety choices (no persistence, HTML escape).

---

## Future improvements

- Add measured latency/cost dashboards
- Expand HITL UX beyond flags

---

## License

See repository.

---

<p align="center">
  <b>AI Job Recommender with MCP Tools</b><br/>
  <a href="https://github.com/ArchanaChetan07/Real-time-Job-recommendation-system---MCP">github.com/ArchanaChetan07/Real-time-Job-recommendation-system---MCP</a>
</p>
