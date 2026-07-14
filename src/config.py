"""Application configuration from environment variables (lazy — no hard fail on import)."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "").strip()

# Demo / offline mode when keys are missing (or DEMO_MODE=1)
DEMO_MODE = os.getenv("DEMO_MODE", "").lower() in {"1", "true", "yes"} or (
    not OPENAI_API_KEY or not APIFY_API_TOKEN
)

HITL_ENABLED = os.getenv("HITL_ENABLED", "1").lower() in {"1", "true", "yes"}
MAX_AGENT_STEPS = int(os.getenv("MAX_AGENT_STEPS", "8"))

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_TIMEOUT_SEC = int(os.getenv("OPENAI_TIMEOUT_SEC", "60"))
OPENAI_MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "3"))

APIFY_TIMEOUT_SEC = int(os.getenv("APIFY_TIMEOUT_SEC", "120"))
APIFY_MAX_RETRIES = int(os.getenv("APIFY_MAX_RETRIES", "2"))

MAX_PDF_SIZE_MB = float(os.getenv("MAX_PDF_SIZE_MB", "10"))
MAX_RESUME_CHARS = int(os.getenv("MAX_RESUME_CHARS", "50000"))

DEFAULT_JOB_ROWS = int(os.getenv("DEFAULT_JOB_ROWS", "60"))
DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "india")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def require_live_keys() -> None:
    """Raise only when a live (non-demo) path needs API credentials."""
    if DEMO_MODE:
        return
    missing = []
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if not APIFY_API_TOKEN:
        missing.append("APIFY_API_TOKEN")
    if missing:
        raise ValueError(
            f"Missing required env vars: {', '.join(missing)}. "
            "Set them in .env or enable DEMO_MODE=1."
        )


def setup_logging() -> None:
    """Configure root logger for the application."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
