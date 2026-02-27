"""Tests for config (env handling)."""

import os

import pytest


def test_config_loads_with_env():
    # conftest sets OPENAI_API_KEY and APIFY_API_TOKEN
    from src import config

    assert config.OPENAI_API_KEY == "sk-test-key"
    assert config.APIFY_API_TOKEN == "apify-test-token"
    assert config.OPENAI_MODEL == "gpt-4o"
    assert config.DEFAULT_JOB_ROWS == 60
