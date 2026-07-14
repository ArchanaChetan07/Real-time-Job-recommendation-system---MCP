"""Tests for job API (stubs + optional mocked Apify)."""

from src.job_api import fetch_linkedin_jobs, fetch_naukri_jobs


def test_fetch_linkedin_jobs_empty_query():
    assert fetch_linkedin_jobs("") == []
    assert fetch_linkedin_jobs("   ") == []


def test_fetch_naukri_jobs_empty_query():
    assert fetch_naukri_jobs("") == []
    assert fetch_naukri_jobs("   ") == []


def test_fetch_linkedin_jobs_demo_stub():
    jobs = fetch_linkedin_jobs("python developer", rows=5)
    assert len(jobs) >= 1
    assert jobs[0]["demo"] is True
    assert "python" in jobs[0]["title"].lower() or "Python" in jobs[0]["title"]


def test_fetch_naukri_jobs_demo_stub():
    jobs = fetch_naukri_jobs("fastapi", rows=5)
    assert len(jobs) >= 1
    assert jobs[0].get("source") == "naukri"


def test_fetch_linkedin_jobs_mocked_live_path(monkeypatch):
    """Force non-demo client path and mock Apify."""
    monkeypatch.setattr("src.job_api.DEMO_MODE", False)

    def fake_call(*, run_input, timeout_secs):
        return {"defaultDatasetId": "fake-dataset-id"}

    class FakeDataset:
        def iterate_items(self):
            return iter(
                [
                    {
                        "title": "Dev",
                        "companyName": "Acme",
                        "location": "India",
                        "link": "https://example.com",
                    }
                ]
            )

    class FakeActor:
        def call(self, *, run_input, timeout_secs=None):
            return fake_call(run_input=run_input, timeout_secs=timeout_secs)

    class FakeClient:
        def actor(self, _id):
            return FakeActor()

        def dataset(self, _id):
            return FakeDataset()

    monkeypatch.setattr("src.job_api.get_apify_client", lambda: FakeClient())
    jobs = fetch_linkedin_jobs("python developer", rows=5)
    assert len(jobs) == 1
    assert jobs[0]["title"] == "Dev"
    assert jobs[0]["companyName"] == "Acme"
