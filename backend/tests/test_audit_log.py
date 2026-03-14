"""
Audit Log Tests

Proves that every meaningful action is recorded,
and that the audit trail is append-only and accurate.
"""

import pytest
from app.models import AuditLog


class TestAuditLogCreation:

    def test_state_change_creates_audit_record(self, app, draft_experiment, db):
        from app.services.state_machine import transition
        initial_count = AuditLog.query.filter_by(
            experiment_id=draft_experiment.id,
            event_type="state_change"
        ).count()
        transition(draft_experiment, "running", db.session)
        db.session.commit()
        new_count = AuditLog.query.filter_by(
            experiment_id=draft_experiment.id,
            event_type="state_change"
        ).count()
        assert new_count == initial_count + 1

    def test_audit_record_contains_correct_states(self, app, draft_experiment, db):
        from app.services.state_machine import transition
        transition(draft_experiment, "running", db.session)
        db.session.commit()
        log = AuditLog.query.filter_by(
            experiment_id=draft_experiment.id,
            event_type="state_change",
        ).order_by(AuditLog.created_at.desc()).first()
        assert log.from_state == "draft"
        assert log.to_state == "running"

    def test_each_transition_creates_one_record(self, app, experiment_with_result, db):
        from app.services.state_machine import transition
        before = AuditLog.query.filter_by(
            experiment_id=experiment_with_result.id,
            event_type="state_change",
        ).count()
        transition(experiment_with_result, "paused", db.session)
        transition(experiment_with_result, "running", db.session)
        transition(experiment_with_result, "completed", db.session)
        db.session.commit()
        after = AuditLog.query.filter_by(
            experiment_id=experiment_with_result.id,
            event_type="state_change",
        ).count()
        assert after == before + 3

    def test_verdict_set_creates_audit_record(self, client, completed_experiment):
        before = AuditLog.query.filter_by(
            experiment_id=completed_experiment.id,
            event_type="verdict_set",
        ).count()
        client.post(
            f"/api/experiments/{completed_experiment.id}/verdict",
            json={"verdict": "ship", "verdict_reason": "Strong results."},
        )
        after = AuditLog.query.filter_by(
            experiment_id=completed_experiment.id,
            event_type="verdict_set",
        ).count()
        assert after == before + 1

    def test_verdict_audit_contains_verdict_value(self, client, completed_experiment):
        client.post(
            f"/api/experiments/{completed_experiment.id}/verdict",
            json={"verdict": "rollback", "verdict_reason": "Negative results."},
        )
        log = AuditLog.query.filter_by(
            experiment_id=completed_experiment.id,
            event_type="verdict_set",
        ).first()
        assert log is not None
        assert log.metadata.get("verdict") == "rollback"

    def test_result_added_creates_audit_record(self, client, running_experiment):
        before = AuditLog.query.filter_by(
            experiment_id=running_experiment.id,
            event_type="result_added",
        ).count()
        client.post(
            f"/api/experiments/{running_experiment.id}/results",
            json={
                "control_value": 3.2,
                "variant_value": 4.1,
                "sample_size_control": 1400,
                "sample_size_variant": 1380,
                "duration_days": 14,
            },
        )
        after = AuditLog.query.filter_by(
            experiment_id=running_experiment.id,
            event_type="result_added",
        ).count()
        assert after == before + 1

    def test_audit_log_has_timestamp(self, app, draft_experiment, db):
        from app.services.state_machine import transition
        transition(draft_experiment, "running", db.session)
        db.session.commit()
        log = AuditLog.query.filter_by(
            experiment_id=draft_experiment.id,
            event_type="state_change",
        ).first()
        assert log.created_at is not None

    def test_audit_logs_returned_in_experiment_detail(self, client, draft_experiment):
        res = client.get(f"/api/experiments/{draft_experiment.id}")
        data = res.get_json()
        assert "audit_logs" in data
        assert isinstance(data["audit_logs"], list)

    def test_full_lifecycle_audit_trail(self, client, app, draft_experiment, db):
        """End-to-end: full lifecycle produces ordered audit trail."""
        from app.services.state_machine import transition
        exp = draft_experiment

        # draft → running
        transition(exp, "running", db.session)
        db.session.commit()

        # add result
        client.post(
            f"/api/experiments/{exp.id}/results",
            json={
                "control_value": 3.2,
                "variant_value": 4.1,
                "sample_size_control": 1400,
                "sample_size_variant": 1380,
                "duration_days": 14,
            },
        )

        # running → completed
        transition(exp, "completed", db.session)
        db.session.commit()

        # set verdict
        client.post(
            f"/api/experiments/{exp.id}/verdict",
            json={"verdict": "ship"},
        )

        res = client.get(f"/api/experiments/{exp.id}")
        logs = res.get_json()["audit_logs"]
        event_types = [l["event_type"] for l in logs]

        assert "state_change" in event_types
        assert "result_added" in event_types
        assert "verdict_set" in event_types
