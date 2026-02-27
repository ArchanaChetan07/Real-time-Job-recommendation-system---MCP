"""PDF extraction and OpenAI integration with validation and resilience."""

import logging
from html import escape

import fitz  # PyMuPDF
from openai import OpenAI

from src.config import (
    MAX_PDF_SIZE_MB,
    MAX_RESUME_CHARS,
    OPENAI_API_KEY,
    OPENAI_MAX_RETRIES,
    OPENAI_MODEL,
    OPENAI_TIMEOUT_SEC,
)

logger = logging.getLogger(__name__)

client = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_TIMEOUT_SEC)


class PDFError(Exception):
    """Raised when PDF processing fails."""

    pass


class OpenAIError(Exception):
    """Raised when OpenAI API fails."""

    pass


def extract_text_from_pdf(uploaded_file, max_size_mb: float | None = None) -> str:
    """
    Extract text from a PDF file with size and content limits.

    Args:
        uploaded_file: File-like object (e.g. Streamlit UploadedFile).
        max_size_mb: Max allowed size in MB (default from config).

    Returns:
        Extracted text.

    Raises:
        PDFError: On invalid/empty PDF or size exceeded.
    """
    max_size_mb = max_size_mb if max_size_mb is not None else MAX_PDF_SIZE_MB
    max_bytes = int(max_size_mb * 1024 * 1024)

    try:
        raw = uploaded_file.read()
    except Exception as e:
        logger.exception("Failed to read uploaded file")
        raise PDFError("Could not read the uploaded file. Please try again.") from e

    if len(raw) > max_bytes:
        raise PDFError(
            f"PDF is too large. Maximum size is {max_size_mb:.0f} MB."
        )

    if len(raw) == 0:
        raise PDFError("The uploaded file is empty.")

    try:
        doc = fitz.open(stream=raw, filetype="pdf")
    except Exception as e:
        logger.warning("PyMuPDF failed to open PDF: %s", e)
        raise PDFError("Invalid or corrupted PDF. Please upload a valid PDF file.") from e

    try:
        text = ""
        for page in doc:
            text += page.get_text()
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


def ask_openai(prompt: str, max_tokens: int = 500) -> str:
    """
    Call OpenAI chat completion with retries and timeout.

    Args:
        prompt: User prompt.
        max_tokens: Max tokens in the response.

    Returns:
        Assistant message content.

    Raises:
        OpenAIError: On API or network failure after retries.
    """
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
