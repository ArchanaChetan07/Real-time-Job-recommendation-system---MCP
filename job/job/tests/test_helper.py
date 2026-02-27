"""Tests for PDF extraction and OpenAI helper (mocked)."""

import io

import fitz
import pytest

from src.helper import PDFError, escape_html, extract_text_from_pdf


def test_escape_html_prevents_xss():
    assert escape_html("hello") == "hello"
    assert "<script>" not in escape_html("<script>alert(1)</script>")
    assert "&lt;script&gt;" in escape_html("<script>alert(1)</script>")
    assert escape_html("a\nb") == "a<br>b"


def test_extract_text_from_pdf_empty_file():
    empty = io.BytesIO(b"")
    with pytest.raises(PDFError, match="empty"):
        extract_text_from_pdf(empty)


def test_extract_text_from_pdf_invalid_pdf():
    not_pdf = io.BytesIO(b"not a pdf content")
    with pytest.raises(PDFError, match="Invalid|corrupted"):
        extract_text_from_pdf(not_pdf)


def test_extract_text_from_pdf_size_limit():
    # Build a valid PDF with text (larger than 1 byte)
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Resume text here")
    pdf_bytes = doc.tobytes()
    doc.close()
    buf = io.BytesIO(pdf_bytes)
    with pytest.raises(PDFError, match="too large"):
        extract_text_from_pdf(buf, max_size_mb=0.000001)


def test_extract_text_from_pdf_success():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Python developer, 5 years")
    pdf_bytes = doc.tobytes()
    doc.close()
    text = extract_text_from_pdf(io.BytesIO(pdf_bytes))
    assert "Python" in text
    assert "developer" in text
