"""Application configuration from environment variables."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (parent of src)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

# ---------------------------------------------------------------------------
# Required
# ---------------------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Add it to your .env file.")
if not APIFY_API_TOKEN:
    raise ValueError("APIFY_API_TOKEN is not set. Add it to your .env file.")

# ---------------------------------------------------------------------------
# Optional with defaults
# ---------------------------------------------------------------------------
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
OPENAI_TIMEOUT_SEC = int(os.getenv("OPENAI_TIMEOUT_SEC", "60"))
OPENAI_MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "3"))

APIFY_TIMEOUT_SEC = int(os.getenv("APIFY_TIMEOUT_SEC", "120"))
APIFY_MAX_RETRIES = int(os.getenv("APIFY_MAX_RETRIES", "2"))

# PDF and content limits (avoid runaway cost and DoS)
MAX_PDF_SIZE_MB = float(os.getenv("MAX_PDF_SIZE_MB", "10"))
MAX_RESUME_CHARS = int(os.getenv("MAX_RESUME_CHARS", "50000"))  # ~12k tokens

# Job fetch defaults
DEFAULT_JOB_ROWS = int(os.getenv("DEFAULT_JOB_ROWS", "60"))
DEFAULT_LOCATION = os.getenv("DEFAULT_LOCATION", "india")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def setup_logging() -> None:
    """Configure root logger for the application."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # Reduce noise from third-party libs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
