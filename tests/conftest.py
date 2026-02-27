"""Pytest fixtures and env for tests (avoid loading real .env)."""

import os

import pytest

# Set env before any test module imports src (so config validation succeeds)
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")
os.environ.setdefault("APIFY_API_TOKEN", "apify-test-token")


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Keep env set for each test."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
    monkeypatch.setenv("APIFY_API_TOKEN", "apify-test-token")
