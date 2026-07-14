"""Agent loop and HITL tests (offline / DEMO_MODE)."""

from src.agent.hitl import apply_approval, request_keyword_approval
from src.agent.loop import run_analyze_phase, run_fetch_phase, run_planning_loop


SAMPLE_RESUME = """
Jane Doe
Software Engineer skilled in Python, FastAPI, Docker, Kubernetes, and LLM tooling.
Built MCP servers and MLOps pipelines. AWS experience.
"""


def test_analyze_phase_awaits_approval():
    result = run_analyze_phase(SAMPLE_RESUME, max_rows=5)
    assert result.awaiting_approval is True
    assert result.state.summary
    assert result.state.keywords
    assert result.trace.spans


def test_full_loop_auto_approve_returns_stub_jobs():
    result = run_planning_loop(SAMPLE_RESUME, auto_approve=True, max_rows=5)
    assert result.status == "ok"
    assert result.state.linkedin_jobs
    assert result.state.naukri_jobs
    assert any(s.name.startswith("tool:") for s in result.trace.spans)


def test_hitl_helpers():
    req = request_keyword_approval("python, fastapi")
    assert "python" in req.message
    ok, override = apply_approval(True, "python, backend")
    assert ok and override == "python, backend"
    ok2, _ = apply_approval(False)
    assert ok2 is False


def test_fetch_requires_approval():
    analyze = run_analyze_phase(SAMPLE_RESUME)
    try:
        run_fetch_phase(analyze.state)
        assert False, "expected ValueError"
    except ValueError:
        pass
