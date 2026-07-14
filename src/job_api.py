"""Job fetching from LinkedIn and Naukri via Apify with retries, plus demo stubs."""

from __future__ import annotations

import logging
import time
from typing import Any

from src.config import (
    APIFY_API_TOKEN,
    APIFY_MAX_RETRIES,
    APIFY_TIMEOUT_SEC,
    DEFAULT_JOB_ROWS,
    DEFAULT_LOCATION,
    DEMO_MODE,
)

logger = logging.getLogger(__name__)

_client: Any = None

LINKEDIN_ACTOR_ID = "BHzefUZlZRKWxkTck"
NAUKRI_ACTOR_ID = "alpcnRV9YI9lYVPWk"


class JobAPIError(Exception):
    """Raised when job fetch fails."""


def get_apify_client():
    global _client
    if DEMO_MODE or not APIFY_API_TOKEN:
        return None
    if _client is None:
        from apify_client import ApifyClient

        _client = ApifyClient(APIFY_API_TOKEN)
    return _client


def _stub_jobs(search_query: str, source: str) -> list[dict]:
    q = (search_query or "software engineer").strip()
    return [
        {
            "title": f"{q.title()} Engineer",
            "companyName": f"{source.title()} Demo Labs",
            "location": DEFAULT_LOCATION,
            "link": f"https://example.com/jobs/{source}/1",
            "url": f"https://example.com/jobs/{source}/1",
            "source": source,
            "demo": True,
        },
        {
            "title": f"Senior {q.title()}",
            "companyName": f"{source.title()} Platform Co",
            "location": DEFAULT_LOCATION,
            "link": f"https://example.com/jobs/{source}/2",
            "url": f"https://example.com/jobs/{source}/2",
            "source": source,
            "demo": True,
        },
    ]


def _call_actor_with_retries(actor_id: str, run_input: dict) -> list:
    client = get_apify_client()
    if client is None:
        raise JobAPIError("Apify client unavailable (demo mode).")

    last_error: Exception | None = None
    for attempt in range(1, APIFY_MAX_RETRIES + 1):
        try:
            run = client.actor(actor_id).call(
                run_input=run_input,
                timeout_secs=APIFY_TIMEOUT_SEC,
            )
            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                raise JobAPIError("Actor run did not return a dataset ID.")
            return list(client.dataset(dataset_id).iterate_items())
        except Exception as e:
            last_error = e
            logger.warning(
                "Apify actor %s attempt %d/%d failed: %s",
                actor_id,
                attempt,
                APIFY_MAX_RETRIES,
                e,
            )
            if attempt < APIFY_MAX_RETRIES:
                time.sleep(2**attempt)
            else:
                break

    raise JobAPIError(
        "Job search is temporarily unavailable. Please try again later."
    ) from last_error


def fetch_linkedin_jobs(
    search_query: str,
    location: str = DEFAULT_LOCATION,
    rows: int = DEFAULT_JOB_ROWS,
) -> list[dict]:
    if not (search_query or "").strip():
        return []
    if DEMO_MODE or get_apify_client() is None:
        return _stub_jobs(search_query, "linkedin")[: min(rows, 10)]

    run_input = {
        "title": search_query.strip(),
        "location": location,
        "rows": min(rows, 100),
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"],
        },
    }
    return _call_actor_with_retries(LINKEDIN_ACTOR_ID, run_input)


def fetch_naukri_jobs(
    search_query: str,
    location: str = DEFAULT_LOCATION,
    rows: int = DEFAULT_JOB_ROWS,
) -> list[dict]:
    if not (search_query or "").strip():
        return []
    if DEMO_MODE or get_apify_client() is None:
        return _stub_jobs(search_query, "naukri")[: min(rows, 10)]

    run_input = {
        "keyword": search_query.strip(),
        "maxJobs": min(rows, 100),
        "freshness": "all",
        "sortBy": "relevance",
        "experience": "all",
    }
    return _call_actor_with_retries(NAUKRI_ACTOR_ID, run_input)
