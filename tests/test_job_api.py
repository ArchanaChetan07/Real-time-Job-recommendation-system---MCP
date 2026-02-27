"""Tests for job API (mocked Apify)."""

import pytest


def test_fetch_linkedin_jobs_empty_query():
    from src.job_api import fetch_linkedin_jobs

    assert fetch_linkedin_jobs("") == []
    assert fetch_linkedin_jobs("   ") == []


def test_fetch_naukri_jobs_empty_query():
    from src.job_api import fetch_naukri_jobs

    assert fetch_naukri_jobs("") == []
    assert fetch_naukri_jobs("   ") == []


def test_fetch_linkedin_jobs_mocked(monkeypatch):
    from src.job_api import fetch_linkedin_jobs

    def fake_call(*, run_input, timeout_secs):
        return {"defaultDatasetId": "fake-dataset-id"}

    def fake_iterate():
        return iter([{"title": "Dev", "companyName": "Acme", "location": "India", "link": "https://example.com"}])

    class FakeDataset:
        def iterate_items(self):
            return fake_iterate()

    class FakeActor:
        def call(self, *, run_input, timeout_secs=None):
            return fake_call(run_input=run_input, timeout_secs=timeout_secs)

    class FakeClient:
        def actor(self, _id):
            return FakeActor()

        def dataset(self, _id):
            return FakeDataset()

    monkeypatch.setattr("src.job_api.client", FakeClient())
    jobs = fetch_linkedin_jobs("python developer", rows=5)
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Dev"
    assert jobs[0]["companyName"] == "Acme"
