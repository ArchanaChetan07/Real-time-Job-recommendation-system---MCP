import asyncio
from fastmcp import FastMCP
from src.job_api import fetch_linkedin_jobs, fetch_naukri_jobs

mcp = FastMCP("Job Recommender")


@mcp.tool()
async def fetchlinkedin(listofkey: str):
    """Fetch LinkedIn jobs by comma-separated search keywords."""
    return await asyncio.to_thread(fetch_linkedin_jobs, listofkey)


@mcp.tool()
async def fetchnaukri(listofkey: str):
    """Fetch Naukri jobs by comma-separated search keywords."""
    return await asyncio.to_thread(fetch_naukri_jobs, listofkey)


if __name__ == "__main__":
    mcp.run(transport="stdio")