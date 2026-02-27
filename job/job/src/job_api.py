"""Job fetching from LinkedIn and Naukri via Apify with retries and error handling."""

import logging
import time

from apify_client import ApifyClient

from src.config import (
    APIFY_API_TOKEN,
    APIFY_MAX_RETRIES,
    APIFY_TIMEOUT_SEC,
    DEFAULT_JOB_ROWS,
    DEFAULT_LOCATION,
)

logger = logging.getLogger(__name__)

client = ApifyClient(APIFY_API_TOKEN)

# Apify actor IDs
LINKEDIN_ACTOR_ID = "BHzefUZlZRKWxkTck"
NAUKRI_ACTOR_ID = "alpcnRV9YI9lYVPWk"


class JobAPIError(Exception):
    """Raised when job fetch fails."""

    pass


def _call_actor_with_retries(actor_id: str, run_input: dict) -> list:
    """Run an Apify actor with retries. Returns list of dataset items."""
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
            items = list(client.dataset(dataset_id).iterate_items())
            return items
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
                time.sleep(2**attempt)  # backoff
            else:
                break

    logger.exception("Apify actor %s failed after %d retries", actor_id, APIFY_MAX_RETRIES)
    raise JobAPIError(
        "Job search is temporarily unavailable. Please try again later."
    ) from last_error


def fetch_linkedin_jobs(
    search_query: str,
    location: str = DEFAULT_LOCATION,
    rows: int = DEFAULT_JOB_ROWS,
) -> list[dict]:
    """
    Fetch LinkedIn jobs from Apify.

    Args:
        search_query: Job title/keywords (comma-separated ok).
        location: Location filter.
        rows: Max number of jobs.

    Returns:
        List of job dicts (e.g. title, companyName, location, link).
    """
    if not (search_query or "").strip():
        return []

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
    """
    Fetch Naukri jobs from Apify.

    Args:
        search_query: Job keywords (comma-separated ok).
        location: Unused by this actor but kept for API consistency.
        rows: Max number of jobs.

    Returns:
        List of job dicts (e.g. title, companyName, location, url).
    """
    if not (search_query or "").strip():
        return []

    run_input = {
        "keyword": search_query.strip(),
        "maxJobs": min(rows, 100),
        "freshness": "all",
        "sortBy": "relevance",
        "experience": "all",
    }
    return _call_actor_with_retries(NAUKRI_ACTOR_ID, run_input)
