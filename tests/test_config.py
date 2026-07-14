"""Tests for config (env handling)."""

from src import config


def test_config_loads_without_keys_in_demo():
    assert config.DEMO_MODE is True
    assert config.OPENAI_MODEL == "gpt-4o"
    assert config.DEFAULT_JOB_ROWS == 60
    assert config.MAX_AGENT_STEPS >= 1


def test_require_live_keys_noop_in_demo():
    config.require_live_keys()  # should not raise
