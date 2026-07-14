"""Plan → tool → observe → revise loop for job recommendations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.agent.planner import create_initial_plan, revise_plan
from src.agent.tools import call_tool
from src.agent.types import AgentState, Observation, Plan
from src.config import MAX_AGENT_STEPS
from src.tracing import Trace, new_run_id, span


@dataclass
class AgentResult:
    state: AgentState
    trace: Trace
    status: str
    message: str = ""
    awaiting_approval: bool = False
    extras: dict[str, Any] = field(default_factory=dict)


def _apply_observation(state: AgentState, obs: Observation) -> None:
    state.observations.append(obs)
    if not obs.ok:
        return
    if obs.tool == "analyze_summary":
        state.summary = str(obs.data or "")
    elif obs.tool == "analyze_skill_gaps":
        state.skill_gaps = str(obs.data or "")
    elif obs.tool == "analyze_roadmap":
        state.roadmap = str(obs.data or "")
    elif obs.tool in {"extract_keywords", "narrow_keywords"}:
        state.keywords = str(obs.data or "").strip()
        # When keywords change during revise, clear jobs so fetch can retry.
        if obs.tool == "narrow_keywords":
            state.linkedin_jobs = []
            state.naukri_jobs = []
    elif obs.tool == "fetch_linkedin":
        state.linkedin_jobs = list(obs.data or [])
    elif obs.tool == "fetch_naukri":
        state.naukri_jobs = list(obs.data or [])


def _execute_plan(state: AgentState, plan: Plan, trace: Trace) -> None:
    for step in plan.steps:
        with span(trace, f"tool:{step.tool}", reason=step.reason) as s:
            try:
                # Keep fetch args in sync with latest keywords after revise.
                args = dict(step.args)
                if step.tool in {"fetch_linkedin", "fetch_naukri"} and state.keywords:
                    args["search_query"] = state.keywords
                result = call_tool(step.tool, **args)
                obs = Observation(tool=step.tool, ok=True, data=result)
                s.attrs["ok"] = True
            except Exception as e:
                obs = Observation(tool=step.tool, ok=False, error=str(e))
                s.attrs["ok"] = False
                s.status = "error"
                s.error = str(e)
            _apply_observation(state, obs)


def run_analyze_phase(resume_text: str, location: str = "india", max_rows: int = 20) -> AgentResult:
    """Run analyze tools and stop for HITL before job fetch."""
    state = AgentState(resume_text=resume_text, location=location, max_rows=max_rows)
    trace = Trace(run_id=new_run_id())
    with span(trace, "phase:analyze"):
        plan = create_initial_plan(state)
        _execute_plan(state, plan, trace)
    state.pending_approval = state.keywords
    return AgentResult(
        state=state,
        trace=trace,
        status="awaiting_approval",
        message="Approve keywords to fetch jobs.",
        awaiting_approval=True,
        extras={"proposed_keywords": state.keywords},
    )


def run_fetch_phase(state: AgentState, previous_trace: Trace | None = None) -> AgentResult:
    """After HITL approval: fetch jobs and revise once if empty."""
    if not state.approved:
        raise ValueError("Cannot fetch jobs without HITL approval.")
    trace = previous_trace or Trace(run_id=new_run_id())
    steps_used = 0
    with span(trace, "phase:fetch_revise"):
        while steps_used < MAX_AGENT_STEPS:
            plan = revise_plan(state)
            if plan is None:
                break
            _execute_plan(state, plan, trace)
            steps_used += len(plan.steps)
            if state.linkedin_jobs or state.naukri_jobs:
                break

    status = "ok" if (state.linkedin_jobs or state.naukri_jobs) else "no_jobs"
    return AgentResult(
        state=state,
        trace=trace,
        status=status,
        message="Job fetch complete." if status == "ok" else "No jobs found after revise.",
        awaiting_approval=False,
    )


def run_planning_loop(
    resume_text: str,
    *,
    location: str = "india",
    max_rows: int = 20,
    auto_approve: bool = False,
    keywords_override: str | None = None,
) -> AgentResult:
    """
    Full loop for non-UI callers / tests.
    If auto_approve=False, returns after analyze for HITL.
    """
    analyze = run_analyze_phase(resume_text, location=location, max_rows=max_rows)
    if not auto_approve:
        return analyze
    state = analyze.state
    state.approved = True
    if keywords_override:
        state.keywords = keywords_override
    return run_fetch_phase(state, previous_trace=analyze.trace)
