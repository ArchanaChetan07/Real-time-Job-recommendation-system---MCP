"""Planner and reviser for the job-recommender agent."""

from __future__ import annotations

from src.agent.types import AgentState, Plan, PlanStep


def create_initial_plan(state: AgentState) -> Plan:
    """Deterministic first plan — analyze resume, then derive keywords (HITL before fetch)."""
    return Plan(
        steps=[
            PlanStep("analyze_summary", {"resume_text": state.resume_text}, "Build candidate summary"),
            PlanStep("analyze_skill_gaps", {"resume_text": state.resume_text}, "Find skill gaps"),
            PlanStep("analyze_roadmap", {"resume_text": state.resume_text}, "Career roadmap"),
            PlanStep("extract_keywords", {"resume_text": state.resume_text}, "Derive search keywords"),
        ],
        notes="phase=analyze",
    )


def revise_plan(state: AgentState) -> Plan | None:
    """Observe → revise: fetch after HITL; if empty, broaden keywords once and retry."""
    if not (state.keywords and state.approved):
        return None

    fetch_steps = [
        PlanStep(
            "fetch_linkedin",
            {
                "search_query": state.keywords,
                "location": state.location,
                "rows": state.max_rows,
            },
            "Fetch LinkedIn jobs",
        ),
        PlanStep(
            "fetch_naukri",
            {
                "search_query": state.keywords,
                "location": state.location,
                "rows": state.max_rows,
            },
            "Fetch Naukri jobs",
        ),
    ]

    # First fetch after approval
    if not state.fetch_attempted:
        state.fetch_attempted = True
        return Plan(steps=fetch_steps, notes="phase=fetch")

    # Empty results → broaden keywords and retry once
    if not (state.linkedin_jobs or state.naukri_jobs) and state.revisions < 1:
        state.revisions += 1
        return Plan(
            steps=[
                PlanStep(
                    "narrow_keywords",
                    {
                        "keywords": state.keywords,
                        "observation_note": "No jobs returned; broaden titles",
                    },
                    "Broaden keywords after empty results",
                ),
                *fetch_steps,
            ],
            notes="phase=revise_empty_jobs",
        )

    return None
