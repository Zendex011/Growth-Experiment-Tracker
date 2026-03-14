"""
Experiment API Endpoint Tests

Tests the HTTP layer: correct status codes, response shapes,
and that invalid requests are rejected before touching the DB.
"""

import json
import pytest


VALID_PAYLOAD = {
    "title": "Green Button Test",
    "hypothesis": "We believe that a green button will increase signups by 15% because it is more visible.",
    "metric_name": "signup_rate",
    "metric_baseline": 3.2,
}


# ── POST /api/experiments ──────────────────────────────────────────────────────

class TestCreateExperiment:

    def test_create_valid_returns_201(self, client):
        res = client.post("/api/experiments/", json=VALID_PAYLOAD)
        assert res.status_code == 201

    def test_create_returns_experiment_shape(self, client):
        res = client.post("/api/experiments/", json=VALID_PAYLOAD)
        data = res.get_json()
        assert "id" in data
        assert data["state"] == "draft"
        assert data["verdict"] is None

    def test_create_missing_title_returns_400(self, client):
        payload = {**VALID_PAYLOAD}
        del payload["title"]
        res = client.post("/api/experiments/", json=payload)
        assert res.status_code == 400

    def test_create_missing_hypothesis_returns_400(self, client):
        payload = {**VALID_PAYLOAD}
        del payload["hypothesis"]
        res = client.post("/api/experiments/", json=payload)
        assert res.status_code == 400

    def test_create_blank_title_returns_400(self, client):
        payload = {**VALID_PAYLOAD, "title": "   "}
        res = client.post("/api/experiments/", json=payload)
        assert res.status_code == 400

    def test_create_short_hypothesis_returns_400(self, client):
        payload = {**VALID_PAYLOAD, "hypothesis": "too short"}
        res = client.post("/api/experiments/", json=payload)
        assert res.status_code == 400

    def test_create_negative_baseline_returns_400(self, client):
        payload = {**VALID_PAYLOAD, "metric_baseline": -1.0}
        res = client.post("/api/experiments/", json=payload)
        assert res.status_code == 400

    def test_create_empty_body_returns_400(self, client):
        res = client.post("/api/experiments/", json={})
        assert res.status_code == 400


# ── GET /api/experiments ───────────────────────────────────────────────────────

class TestListExperiments:

    def test_list_empty_returns_200(self, client):
        res = client.get("/api/experiments/")
        assert res.status_code == 200
        assert res.get_json() == []

    def test_list_returns_created_experiments(self, client):
        client.post("/api/experiments/", json=VALID_PAYLOAD)
        client.post("/api/experiments/", json={**VALID_PAYLOAD, "title": "Second Test"})
        res = client.get("/api/experiments/")
        assert len(res.get_json()) == 2

    def test_list_filter_by_state(self, client, running_experiment):
        client.post("/api/experiments/", json=VALID_PAYLOAD)  # creates another draft
        res = client.get("/api/experiments/?state=running")
        data = res.get_json()
        assert all(e["state"] == "running" for e in data)
        assert len(data) == 1


# ── GET /api/experiments/:id ───────────────────────────────────────────────────

class TestGetExperiment:

    def test_get_existing_returns_200(self, client, draft_experiment):
        res = client.get(f"/api/experiments/{draft_experiment.id}")
        assert res.status_code == 200
        assert res.get_json()["id"] == draft_experiment.id

    def test_get_includes_results_and_audit(self, client, draft_experiment):
        res = client.get(f"/api/experiments/{draft_experiment.id}")
        data = res.get_json()
        assert "results" in data
        assert "audit_logs" in data

    def test_get_nonexistent_returns_404(self, client):
        res = client.get("/api/experiments/nonexistent-id")
        assert res.status_code == 404

    def test_error_response_has_correct_shape(self, client):
        res = client.get("/api/experiments/nonexistent-id")
        data = res.get_json()
        assert "error" in data
        assert "message" in data
        assert "status" in data


# ── PATCH /api/experiments/:id/state ──────────────────────────────────────────

class TestUpdateState:

    def test_valid_transition_returns_200(self, client, draft_experiment):
        res = client.patch(
            f"/api/experiments/{draft_experiment.id}/state",
            json={"state": "running"},
        )
        assert res.status_code == 200
        assert res.get_json()["state"] == "running"

    def test_response_includes_allowed_next(self, client, draft_experiment):
        res = client.patch(
            f"/api/experiments/{draft_experiment.id}/state",
            json={"state": "running"},
        )
        data = res.get_json()
        assert "allowed_next" in data
        assert set(data["allowed_next"]) == {"paused", "completed"}

    def test_invalid_transition_returns_422(self, client, draft_experiment):
        res = client.patch(
            f"/api/experiments/{draft_experiment.id}/state",
            json={"state": "completed"},
        )
        assert res.status_code == 422

    def test_missing_state_field_returns_400(self, client, draft_experiment):
        res = client.patch(
            f"/api/experiments/{draft_experiment.id}/state",
            json={},
        )
        assert res.status_code == 400

    def test_unknown_state_value_returns_400(self, client, draft_experiment):
        res = client.patch(
            f"/api/experiments/{draft_experiment.id}/state",
            json={"state": "limbo"},
        )
        assert res.status_code == 400

    def test_complete_without_results_returns_422(self, client, running_experiment):
        res = client.patch(
            f"/api/experiments/{running_experiment.id}/state",
            json={"state": "completed"},
        )
        assert res.status_code == 422


# ── DELETE /api/experiments/:id ───────────────────────────────────────────────

class TestDeleteExperiment:

    def test_delete_draft_returns_200(self, client, draft_experiment):
        res = client.delete(f"/api/experiments/{draft_experiment.id}")
        assert res.status_code == 200

    def test_deleted_experiment_not_found(self, client, draft_experiment):
        client.delete(f"/api/experiments/{draft_experiment.id}")
        res = client.get(f"/api/experiments/{draft_experiment.id}")
        assert res.status_code == 404

    def test_delete_running_experiment_returns_409(self, client, running_experiment):
        res = client.delete(f"/api/experiments/{running_experiment.id}")
        assert res.status_code == 409

    def test_delete_nonexistent_returns_404(self, client):
        res = client.delete("/api/experiments/ghost-id")
        assert res.status_code == 404


# ── POST /api/experiments/:id/verdict ─────────────────────────────────────────

class TestSetVerdict:

    def test_set_verdict_on_completed_returns_200(self, client, completed_experiment):
        res = client.post(
            f"/api/experiments/{completed_experiment.id}/verdict",
            json={"verdict": "ship", "verdict_reason": "Strong positive signal."},
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data["verdict"] == "ship"

    def test_set_verdict_on_running_returns_409(self, client, running_experiment):
        res = client.post(
            f"/api/experiments/{running_experiment.id}/verdict",
            json={"verdict": "ship"},
        )
        assert res.status_code == 409

    def test_verdict_locked_after_set(self, client, completed_experiment):
        client.post(
            f"/api/experiments/{completed_experiment.id}/verdict",
            json={"verdict": "ship"},
        )
        res = client.post(
            f"/api/experiments/{completed_experiment.id}/verdict",
            json={"verdict": "rollback"},
        )
        assert res.status_code == 409

    def test_invalid_verdict_value_returns_400(self, client, completed_experiment):
        res = client.post(
            f"/api/experiments/{completed_experiment.id}/verdict",
            json={"verdict": "maybe"},
        )
        assert res.status_code == 400
