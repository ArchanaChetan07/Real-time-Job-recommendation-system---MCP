"""Pytest fixtures — force demo mode for offline green runs."""

import os

import pytest

os.environ["DEMO_MODE"] = "1"
os.environ.setdefault("OPENAI_API_KEY", "")
os.environ.setdefault("APIFY_API_TOKEN", "")


@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    monkeypatch.setenv("DEMO_MODE", "1")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    monkeypatch.setenv("APIFY_API_TOKEN", "")
