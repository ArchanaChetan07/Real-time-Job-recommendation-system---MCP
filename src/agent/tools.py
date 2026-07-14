"""Tool registry for the job-recommender agent."""

from __future__ import annotations

from typing import Any, Callable

from src.helper import ask_openai
from src.job_api import fetch_linkedin_jobs, fetch_naukri_jobs


ToolFn = Callable[..., Any]


def analyze_summary(resume_text: str) -> str:
    return ask_openai(
        f"Summarize this resume in 5 sentences focusing on skills and experience:\n\n{resume_text}",
        max_tokens=400,
    )


def analyze_skill_gaps(resume_text: str) -> str:
    return ask_openai(
        f"Identify skill gaps and missing certifications for stronger candidacy:\n\n{resume_text}",
        max_tokens=400,
    )


def analyze_roadmap(resume_text: str) -> str:
    return ask_openai(
        f"Create a 30/60/90-day career roadmap based on this resume:\n\n{resume_text}",
        max_tokens=500,
    )


def extract_keywords(resume_text: str) -> str:
    return ask_openai(
        "Extract 3-6 comma-separated job-search keywords (titles/skills) from this resume. "
        f"Return ONLY the comma-separated list.\n\n{resume_text}",
        max_tokens=80,
    )


def narrow_keywords(keywords: str, observation_note: str) -> str:
    return ask_openai(
        "Revise these job-search keywords to be broader or more marketable given the note. "
        f"Return ONLY a comma-separated list.\nKeywords: {keywords}\nNote: {observation_note}",
        max_tokens=80,
    )


TOOLS: dict[str, ToolFn] = {
    "analyze_summary": analyze_summary,
    "analyze_skill_gaps": analyze_skill_gaps,
    "analyze_roadmap": analyze_roadmap,
    "extract_keywords": extract_keywords,
    "narrow_keywords": narrow_keywords,
    "fetch_linkedin": fetch_linkedin_jobs,
    "fetch_naukri": fetch_naukri_jobs,
}


def call_tool(name: str, **kwargs: Any) -> Any:
    if name not in TOOLS:
        raise KeyError(f"Unknown tool: {name}")
    return TOOLS[name](**kwargs)
