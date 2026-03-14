"""
AI Service Tests

Key principle: we do NOT test what the AI says.
We test how our system behaves around the AI:
  - valid responses are parsed and returned correctly
  - invalid/missing JSON returns degraded=True gracefully
  - timeouts return degraded=True gracefully
  - 503s return degraded=True gracefully
  - AI failures never cause a 500 response
  - AI output is never auto-saved (tested via endpoint tests)
"""

import pytest


# ── /api/ai/hypothesis ─────────────────────────────────────────────────────────

class TestHypothesisEndpoint:

    def test_valid_response_parsed_correctly(self, client, mock_hf_hypothesis):
        res = client.post(
            "/api/ai/hypothesis",
            json={"rough_idea": "change the signup button colour to green"},
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["degraded"] is False
        assert data["hypothesis"] is not None
        assert "We believe" in data["hypothesis"]

    def test_missing_rough_idea_returns_400(self, client):
        res = client.post("/api/ai/hypothesis", json={})
        assert res.status_code == 400

    def test_too_short_rough_idea_returns_400(self, client):
        res = client.post("/api/ai/hypothesis", json={"rough_idea": "ok"})
        assert res.status_code == 400

    def test_timeout_returns_200_with_degraded(self, client, mock_hf_timeout):
        res = client.post(
            "/api/ai/hypothesis",
            json={"rough_idea": "change the signup button colour to green"},
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["degraded"] is True
        assert data["hypothesis"] is None
        assert "reason" in data

    def test_503_returns_200_with_degraded(self, client, mock_hf_503):
        res = client.post(
            "/api/ai/hypothesis",
            json={"rough_idea": "change the signup button colour to green"},
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["degraded"] is True

    def test_bad_json_returns_200_with_degraded(self, client, mock_hf_bad_json):
        res = client.post(
            "/api/ai/hypothesis",
            json={"rough_idea": "change the signup button colour to green"},
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["degraded"] is True

    def test_ai_failure_never_returns_500(self, client, mock_hf_timeout):
        """AI failure must never propagate as a server error."""
        res = client.post(
            "/api/ai/hypothesis",
            json={"rough_idea": "change the signup button colour to green"},
        )
        assert res.status_code != 500


# ── /api/ai/suggest-verdict ────────────────────────────────────────────────────

class TestVerdictEndpoint:

    VALID_PAYLOAD = {
        "metric_name": "signup_rate",
        "control_value": 3.2,
        "variant_value": 4.1,
        "sample_size_control": 1400,
        "sample_size_variant": 1380,
        "duration_days": 14,
    }

    def test_valid_response_parsed_correctly(self, client, mock_hf_verdict):
        res = client.post("/api/ai/suggest-verdict", json=self.VALID_PAYLOAD)
        assert res.status_code == 200
        data = res.get_json()
        assert data["degraded"] is False
        assert data["verdict"] in ("ship", "rollback", "iterate")
        assert data["interpretation"] is not None

    def test_missing_metric_name_returns_400(self, client):
        payload = {**self.VALID_PAYLOAD}
        del payload["metric_name"]
        res = client.post("/api/ai/suggest-verdict", json=payload)
        assert res.status_code == 400

    def test_timeout_returns_degraded(self, client, mock_hf_timeout):
        res = client.post("/api/ai/suggest-verdict", json=self.VALID_PAYLOAD)
        assert res.status_code == 200
        assert res.get_json()["degraded"] is True

    def test_bad_json_returns_degraded(self, client, mock_hf_bad_json):
        res = client.post("/api/ai/suggest-verdict", json=self.VALID_PAYLOAD)
        assert res.status_code == 200
        assert res.get_json()["degraded"] is True


# ── /api/ai/summarize/:id ──────────────────────────────────────────────────────

class TestSummarizeEndpoint:

    def test_summary_for_completed_experiment(self, client, completed_experiment, mock_hf_summary):
        res = client.post(f"/api/ai/summarize/{completed_experiment.id}")
        assert res.status_code == 200
        data = res.get_json()
        assert data["degraded"] is False
        assert data["summary"] is not None

    def test_summary_for_running_experiment_returns_409(self, client, running_experiment, mock_hf_summary):
        res = client.post(f"/api/ai/summarize/{running_experiment.id}")
        assert res.status_code == 409

    def test_summary_for_draft_experiment_returns_409(self, client, draft_experiment, mock_hf_summary):
        res = client.post(f"/api/ai/summarize/{draft_experiment.id}")
        assert res.status_code == 409

    def test_summary_for_nonexistent_returns_404(self, client, mock_hf_summary):
        res = client.post("/api/ai/summarize/ghost-id")
        assert res.status_code == 404

    def test_timeout_returns_degraded_not_500(self, client, completed_experiment, mock_hf_timeout):
        res = client.post(f"/api/ai/summarize/{completed_experiment.id}")
        assert res.status_code == 200
        assert res.get_json()["degraded"] is True
