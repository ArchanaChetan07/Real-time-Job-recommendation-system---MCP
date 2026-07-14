"""
AI Job Recommender – Streamlit application (plan → HITL → fetch agent loop).

Run from project root:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from src.agent.hitl import apply_approval, request_keyword_approval
from src.agent.loop import run_analyze_phase, run_fetch_phase
from src.config import DEMO_MODE, DEFAULT_JOB_ROWS, setup_logging
from src.helper import PDFError, escape_html, extract_text_from_pdf

setup_logging()

st.set_page_config(
    page_title="AI Job Recommender",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.title("AI Job Recommender")
st.caption("Planning agent: analyze → approve keywords → fetch & revise · MCP-ready")

if DEMO_MODE:
    st.info("Running in **DEMO_MODE** (no live OpenAI/Apify keys). Using heuristic analysis and stub jobs.")

st.markdown(
    "Upload a resume (PDF). The agent builds a plan, derives search keywords, "
    "waits for your approval (HITL), then fetches LinkedIn/Naukri listings and revises if empty."
)

uploaded_file = st.file_uploader("Upload resume (PDF)", type=["pdf"])

if uploaded_file:
    try:
        with st.spinner("Extracting text from your resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)
    except PDFError as e:
        st.error(str(e))
        st.stop()

    if "agent_analyze" not in st.session_state or st.session_state.get("resume_digest") != hash(resume_text):
        with st.spinner("Agent analyzing resume (plan → tools)..."):
            result = run_analyze_phase(resume_text, max_rows=DEFAULT_JOB_ROWS)
        st.session_state["agent_analyze"] = result
        st.session_state["resume_digest"] = hash(resume_text)
        st.session_state.pop("agent_fetch", None)

    analyze = st.session_state["agent_analyze"]
    state = analyze.state

    st.subheader("Resume Summary")
    st.markdown(f"<div style='border:1px solid #ccc;padding:10px'>{escape_html(state.summary)}</div>", unsafe_allow_html=True)
    st.subheader("Skill Gaps")
    st.markdown(f"<div style='border:1px solid #ccc;padding:10px'>{escape_html(state.skill_gaps)}</div>", unsafe_allow_html=True)
    st.subheader("Career Roadmap")
    st.markdown(f"<div style='border:1px solid #ccc;padding:10px'>{escape_html(state.roadmap)}</div>", unsafe_allow_html=True)

    approval = request_keyword_approval(state.keywords or "")
    st.subheader("HITL — Approve job search")
    st.write(approval.message)
    edited = st.text_input("Keywords (editable)", value=state.keywords or "")
    col1, col2 = st.columns(2)
    approve = col1.button("Approve & fetch jobs", type="primary")
    reject = col2.button("Reject")

    if reject:
        st.warning("Fetch cancelled. Edit keywords and approve when ready.")
        st.stop()

    if approve:
        ok, override = apply_approval(True, edited)
        if not ok:
            st.stop()
        state.approved = True
        if override:
            state.keywords = override
        with st.spinner("Agent fetching jobs (observe → revise if empty)..."):
            fetch = run_fetch_phase(state, previous_trace=analyze.trace)
        st.session_state["agent_fetch"] = fetch

    fetch = st.session_state.get("agent_fetch")
    if fetch:
        st.subheader("LinkedIn Jobs")
        for job in fetch.state.linkedin_jobs:
            title = escape_html(str(job.get("title", "")))
            company = escape_html(str(job.get("companyName", "")))
            loc = escape_html(str(job.get("location", "")))
            link = job.get("link") or job.get("url") or "#"
            st.markdown(f"**{title}** at {company} — {loc}  \n[Open]({link})")
        st.subheader("Naukri Jobs")
        for job in fetch.state.naukri_jobs:
            title = escape_html(str(job.get("title", "")))
            company = escape_html(str(job.get("companyName", "")))
            loc = escape_html(str(job.get("location", "")))
            link = job.get("url") or job.get("link") or "#"
            st.markdown(f"**{title}** at {company} — {loc}  \n[Open]({link})")
        with st.expander("Agent trace"):
            st.json(fetch.trace.to_dict())
