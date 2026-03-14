"""
Result API Tests

Proves that results can only be added to running experiments,
and that invalid values are rejected at the schema boundary.
"""

import pytest

VALID_RESULT = {
    "control_value": 3.2,
    "variant_value": 4.1,
    "sample_size_control": 1400,
    "sample_size_variant": 1380,
    "duration_days": 14,
}


class TestAddResult:

    def test_add_result_to_running_returns_201(self, client, running_experiment):
        res = client.post(
            f"/api/experiments/{running_experiment.id}/results",
            json=VALID_RESULT,
        )
        assert res.status_code == 201

    def test_result_response_shape(self, client, running_experiment):
        res = client.post(
            f"/api/experiments/{running_experiment.id}/results",
            json=VALID_RESULT,
        )
        data = res.get_json()
        assert "id" in data
        assert "control_value" in data
        assert "variant_value" in data
        assert "recorded_at" in data

    def test_add_result_to_draft_returns_409(self, client, draft_experiment):
        res = client.post(
            f"/api/experiments/{draft_experiment.id}/results",
            json=VALID_RESULT,
        )
        assert res.status_code == 409

    def test_add_result_to_completed_returns_409(self, client, completed_experiment):
        res = client.post(
            f"/api/experiments/{completed_experiment.id}/results",
            json=VALID_RESULT,
        )
        assert res.status_code == 409

    def test_add_result_to_paused_returns_409(self, client, running_experiment, db):
        from app.services.state_machine import transition
        transition(running_experiment, "paused", db.session)
        db.session.commit()
        res = client.post(
            f"/api/experiments/{running_experiment.id}/results",
            json=VALID_RESULT,
        )
        assert res.status_code == 409

    def test_negative_sample_size_returns_400(self, client, running_experiment):
        res = client.post(
            f"/api/experiments/{running_experiment.id}/results",
            json={**VALID_RESULT, "sample_size_control": -1},
        )
        assert res.status_code == 400

    def test_zero_sample_size_returns_400(self, client, running_experiment):
        res = client.post(
            f"/api/experiments/{running_experiment.id}/results",
            json={**VALID_RESULT, "sample_size_control": 0},
        )
        assert res.status_code == 400

    def test_zero_duration_returns_400(self, client, running_experiment):
        res = client.post(
            f"/api/experiments/{running_experiment.id}/results",
            json={**VALID_RESULT, "duration_days": 0},
        )
        assert res.status_code == 400

    def test_negative_duration_returns_400(self, client, running_experiment):
        res = client.post(
            f"/api/experiments/{running_experiment.id}/results",
            json={**VALID_RESULT, "duration_days": -5},
        )
        assert res.status_code == 400

    def test_missing_control_value_returns_400(self, client, running_experiment):
        payload = {**VALID_RESULT}
        del payload["control_value"]
        res = client.post(
            f"/api/experiments/{running_experiment.id}/results",
            json=payload,
        )
        assert res.status_code == 400

    def test_nonexistent_experiment_returns_404(self, client):
        res = client.post(
            "/api/experiments/ghost-id/results",
            json=VALID_RESULT,
        )
        assert res.status_code == 404


class TestListResults:

    def test_list_results_empty(self, client, running_experiment):
        res = client.get(f"/api/experiments/{running_experiment.id}/results")
        assert res.status_code == 200
        assert res.get_json() == []

    def test_list_results_after_adding(self, client, running_experiment):
        client.post(
            f"/api/experiments/{running_experiment.id}/results",
            json=VALID_RESULT,
        )
        res = client.get(f"/api/experiments/{running_experiment.id}/results")
        assert len(res.get_json()) == 1

    def test_multiple_results_returned(self, client, running_experiment):
        for _ in range(3):
            client.post(
                f"/api/experiments/{running_experiment.id}/results",
                json=VALID_RESULT,
            )
        res = client.get(f"/api/experiments/{running_experiment.id}/results")
        assert len(res.get_json()) == 3
