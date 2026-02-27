"""
AI Job Recommender – Streamlit application.

Resume analysis and job recommendations. Run from project root:
    streamlit run app.py
"""

import streamlit as st

from src.config import DEFAULT_JOB_ROWS, setup_logging
from src.helper import (
    OpenAIError,
    PDFError,
    ask_openai,
    escape_html,
    extract_text_from_pdf,
)
from src.job_api import JobAPIError, fetch_linkedin_jobs, fetch_naukri_jobs

setup_logging()

st.set_page_config(
    page_title="AI Job Recommender",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.title("AI Job Recommender")
st.caption("Resume analysis and job recommendations powered by AI")
st.markdown(
    "Upload your resume (PDF) to receive an automated **summary**, **skill-gap analysis**, "
    "**career roadmap**, and **job listings** from LinkedIn and Naukri."
)

with st.expander("Data & privacy", expanded=False):
    st.markdown(
        "Resume text is sent to **OpenAI** (GPT) for analysis. Job data is fetched via **Apify** "
        "from LinkedIn and Naukri. This application does not store your resume. "
        "Do not upload content you are not comfortable sharing with these services."
    )

uploaded_file = st.file_uploader(
    "Upload resume (PDF)",
    type=["pdf"],
    help="Maximum 10 MB. Text-based PDFs give the best results.",
)

if uploaded_file:
    try:
        with st.spinner("Extracting text from your resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)
    except PDFError as e:
        st.error(str(e))
        st.stop()

    try:
        with st.spinner("Summarizing your resume..."):
            summary = ask_openai(
                f"Summarize this resume highlighting the skills, education, and experience:\n\n{resume_text}",
                max_tokens=500,
            )
    except OpenAIError as e:
        st.error(str(e))
        st.stop()

    try:
        with st.spinner("Finding skill gaps..."):
            gaps = ask_openai(
                f"Analyze this resume and highlight missing skills, certifications, and experiences needed for better job opportunities:\n\n{resume_text}",
                max_tokens=400,
            )
    except OpenAIError as e:
        st.error(str(e))
        st.stop()

    try:
        with st.spinner("Creating future roadmap..."):
            roadmap = ask_openai(
                f"Based on this resume, suggest a future roadmap to improve this person's career prospects (skills to learn, certifications, industry exposure):\n\n{resume_text}",
                max_tokens=400,
            )
    except OpenAIError as e:
        st.error(str(e))
        st.stop()

    # Safe display: escape user/LLM content to prevent XSS
    def _block(content: str) -> str:
        escaped = escape_html(content)
        return f"<div style='background-color:#1e1e1e;padding:15px;border-radius:10px;font-size:16px;color:#eee;'>{escaped}</div>"

    st.markdown("---")
    st.header("Resume summary")
    st.markdown(_block(summary), unsafe_allow_html=True)

    st.markdown("---")
    st.header("Skill gaps & areas to develop")
    st.markdown(_block(gaps), unsafe_allow_html=True)

    st.markdown("---")
    st.header("Career roadmap & preparation")
    st.markdown(_block(roadmap), unsafe_allow_html=True)

    st.success("Analysis completed.")

    if st.button("Get job recommendations"):
        try:
            with st.spinner("Fetching job recommendations..."):
                keywords = ask_openai(
                    f"Based on this resume summary, suggest the best job titles and keywords for searching jobs. Give a comma-separated list only, no explanation.\n\nSummary: {summary}",
                    max_tokens=100,
                )
        except OpenAIError as e:
            st.error(str(e))
        else:
            search_keywords_clean = keywords.replace("\n", "").strip()
            st.success(f"Extracted job keywords: {search_keywords_clean}")

            try:
                with st.spinner("Fetching jobs from LinkedIn and Naukri..."):
                    linkedin_jobs = fetch_linkedin_jobs(
                        search_keywords_clean, rows=DEFAULT_JOB_ROWS
                    )
                    naukri_jobs = fetch_naukri_jobs(
                        search_keywords_clean, rows=DEFAULT_JOB_ROWS
                    )
            except JobAPIError as e:
                st.error(str(e))
            else:
                st.markdown("---")
                st.header("LinkedIn jobs")
                if linkedin_jobs:
                    for job in linkedin_jobs:
                        title = job.get("title") or "—"
                        company = job.get("companyName") or "—"
                        location = job.get("location") or "—"
                        link = job.get("link") or "#"
                        st.markdown(f"**{title}** at *{company}*")
                        st.markdown(f"- 📍 {location}")
                        st.markdown(f"- 🔗 [View Job]({link})")
                        st.markdown("---")
                else:
                    st.warning("No LinkedIn jobs found.")

                st.markdown("---")
                st.header("Naukri jobs (India)")
                if naukri_jobs:
                    for job in naukri_jobs:
                        title = job.get("title") or "—"
                        company = job.get("companyName") or "—"
                        location = job.get("location") or "—"
                        url = job.get("url") or "#"
                        st.markdown(f"**{title}** at *{company}*")
                        st.markdown(f"- 📍 {location}")
                        st.markdown(f"- 🔗 [View Job]({url})")
                        st.markdown("---")
                else:
                    st.warning("No Naukri jobs found.")

st.markdown("---")
st.caption("AI Job Recommender · Resume analysis and job search via OpenAI and Apify")
