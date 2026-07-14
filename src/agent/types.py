"""Typed structures for the job-recommender planning agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlanStep:
    tool: str
    args: dict[str, Any]
    reason: str = ""


@dataclass
class Plan:
    steps: list[PlanStep]
    notes: str = ""


@dataclass
class Observation:
    tool: str
    ok: bool
    data: Any = None
    error: str | None = None


@dataclass
class AgentState:
    resume_text: str
    location: str = "india"
    max_rows: int = 20
    summary: str = ""
    skill_gaps: str = ""
    roadmap: str = ""
    keywords: str = ""
    linkedin_jobs: list[dict] = field(default_factory=list)
    naukri_jobs: list[dict] = field(default_factory=list)
    pending_approval: str | None = None
    approved: bool = False
    fetch_attempted: bool = False
    observations: list[Observation] = field(default_factory=list)
    revisions: int = 0
