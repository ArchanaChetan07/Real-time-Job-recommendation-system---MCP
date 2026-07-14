"""PDF extraction and OpenAI integration with validation, resilience, and demo stubs."""

from __future__ import annotations

import logging
import re
from html import escape
from typing import Any

import fitz  # PyMuPDF

from src.config import (
    DEMO_MODE,
    MAX_PDF_SIZE_MB,
    MAX_RESUME_CHARS,
    OPENAI_API_KEY,
    OPENAI_MAX_RETRIES,
    OPENAI_MODEL,
    OPENAI_TIMEOUT_SEC,
)

logger = logging.getLogger(__name__)

_client: Any = None


class PDFError(Exception):
    """Raised when PDF processing fails."""


class OpenAIError(Exception):
    """Raised when OpenAI API fails."""


def get_openai_client():
    """Lazy OpenAI client — None in demo mode."""
    global _client
    if DEMO_MODE or not OPENAI_API_KEY:
        return None
    if _client is None:
        from openai import OpenAI

        _client = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_TIMEOUT_SEC)
    return _client


def extract_text_from_pdf(uploaded_file, max_size_mb: float | None = None) -> str:
    """Extract text from a PDF file with size and content limits."""
    max_size_mb = max_size_mb if max_size_mb is not None else MAX_PDF_SIZE_MB
    max_bytes = int(max_size_mb * 1024 * 1024)

    try:
        raw = uploaded_file.read()
    except Exception as e:
        logger.exception("Failed to read uploaded file")
        raise PDFError("Could not read the uploaded file. Please try again.") from e

    if len(raw) > max_bytes:
        raise PDFError(f"PDF is too large. Maximum size is {max_size_mb:.0f} MB.")
    if len(raw) == 0:
        raise PDFError("The uploaded file is empty.")

    try:
        doc = fitz.open(stream=raw, filetype="pdf")
    except Exception as e:
        logger.warning("PyMuPDF failed to open PDF: %s", e)
        raise PDFError("Invalid or corrupted PDF. Please upload a valid PDF file.") from e

    try:
        text = "".join(page.get_text() for page in doc)
        doc.close()
    except Exception as e:
        logger.exception("Failed to extract text from PDF")
        raise PDFError("Failed to extract text from the PDF.") from e

    text = text.strip()
    if not text:
        raise PDFError("No text could be extracted from the PDF. It may be image-only.")

    if len(text) > MAX_RESUME_CHARS:
        logger.warning("Resume truncated from %d to %d chars", len(text), MAX_RESUME_CHARS)
        text = text[:MAX_RESUME_CHARS] + "\n\n[Text truncated for processing.]"
    return text


def _heuristic_resume_analyze(prompt: str) -> str:
    """Offline stub responses so demos/tests work without OpenAI."""
    lower = prompt.lower()
    skills = sorted(set(re.findall(
        r"\b(python|java|fastapi|django|kubernetes|docker|aws|sql|react|mcp|llm|mlops)\b",
        lower,
        flags=re.I,
    )))
    skill_str = ", ".join(skills) or "software engineering, python"
    if "skill gap" in lower or "missing skill" in lower:
        return (
            f"Based on the resume ({skill_str}), gaps often include: "
            "system design, cloud certifications, and quantified impact metrics."
        )
    if "roadmap" in lower or "career" in lower:
        return (
            "30-day: refresh DSA + one system-design case study.\n"
            "60-day: ship a portfolio agent with evals + MCP tools.\n"
            "90-day: target platform/ML infra interviews with measured projects."
        )
    if "keyword" in lower or "job title" in lower or "search" in lower:
        base = skills[:4] if skills else ["python", "backend", "fastapi"]
        return ", ".join(base + ["software engineer"])
    return (
        f"Candidate profile emphasizing: {skill_str}. "
        "Experience spans applied ML and backend systems with delivery ownership."
    )


def ask_openai(prompt: str, max_tokens: int = 500) -> str:
    """Call OpenAI chat completion with retries; fall back to heuristic in DEMO_MODE."""
    client = get_openai_client()
    if client is None:
        return _heuristic_resume_analyze(prompt)

    last_error: Exception | None = None
    for attempt in range(1, OPENAI_MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            last_error = e
            logger.warning(
                "OpenAI request attempt %d/%d failed: %s",
                attempt,
                OPENAI_MAX_RETRIES,
                e,
            )
            if attempt == OPENAI_MAX_RETRIES:
                break

    logger.exception("OpenAI request failed after %d retries", OPENAI_MAX_RETRIES)
    msg = "The AI service is temporarily unavailable. Please try again later."
    if last_error:
        msg += f" ({type(last_error).__name__})"
    raise OpenAIError(msg) from last_error


def escape_html(text: str) -> str:
    """Escape string for safe use inside HTML (prevents XSS)."""
    return escape(text).replace("\n", "<br>")
