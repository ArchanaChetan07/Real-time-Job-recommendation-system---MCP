"""HITL approval gate for expensive / side-effectful agent steps."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ApprovalRequest:
    action: str
    payload: str
    message: str


def request_keyword_approval(keywords: str) -> ApprovalRequest:
    return ApprovalRequest(
        action="fetch_jobs",
        payload=keywords,
        message=(
            f"Proposed job-search keywords: {keywords}. "
            "Approve to spend Apify quota / fetch live listings."
        ),
    )


def apply_approval(approved: bool, edited_keywords: str | None = None) -> tuple[bool, str | None]:
    """Return (approved, keywords_override)."""
    if not approved:
        return False, None
    if edited_keywords is not None and edited_keywords.strip():
        return True, edited_keywords.strip()
    return True, None
