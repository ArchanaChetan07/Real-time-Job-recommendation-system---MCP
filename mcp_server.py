"""MCP server exposing job tools + full planning-agent entrypoint."""

from __future__ import annotations

import asyncio

from fastmcp import FastMCP

from src.agent.loop import run_planning_loop
from src.job_api import fetch_linkedin_jobs, fetch_naukri_jobs

mcp = FastMCP("Job Recommender Agent")


@mcp.tool()
async def fetchlinkedin(listofkey: str):
    """Fetch LinkedIn jobs by comma-separated search keywords."""
    return await asyncio.to_thread(fetch_linkedin_jobs, listofkey)


@mcp.tool()
async def fetchnaukri(listofkey: str):
    """Fetch Naukri jobs by comma-separated search keywords."""
    return await asyncio.to_thread(fetch_naukri_jobs, listofkey)


@mcp.tool()
async def run_job_agent(resume_text: str, auto_approve: bool = True, keywords: str = ""):
    """
    Run the plan→analyze→(HITL)→fetch→revise agent.

    For unattended MCP use, auto_approve=True. Pass keywords to override derived search terms.
    """
    def _run():
        result = run_planning_loop(
            resume_text,
            auto_approve=auto_approve,
            keywords_override=keywords or None,
        )
        return {
            "status": result.status,
            "awaiting_approval": result.awaiting_approval,
            "summary": result.state.summary,
            "skill_gaps": result.state.skill_gaps,
            "roadmap": result.state.roadmap,
            "keywords": result.state.keywords,
            "linkedin_jobs": result.state.linkedin_jobs,
            "naukri_jobs": result.state.naukri_jobs,
            "trace": result.trace.to_dict(),
        }

    return await asyncio.to_thread(_run)


if __name__ == "__main__":
    mcp.run(transport="stdio")
