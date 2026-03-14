"""
State Machine Tests

These tests are the most important in the project.
They prove that invalid states are impossible, not just unlikely.

Each valid transition has a passing test.
Each invalid transition has a blocking test.
"""

import pytest
from app.services.state_machine import transition, allowed_transitions, VALID_TRANSITIONS
from app.errors import InvalidTransitionError, ResultRequiredError


# ── Valid Transitions ──────────────────────────────────────────────────────────

class TestValidTransitions:

    def test_draft_to_running(self, app, draft_experiment, db):
        transition(draft_experiment, "running", db.session)
        assert draft_experiment.state == "running"

    def test_running_to_paused(self, app, running_experiment, db):
        transition(running_experiment, "paused", db.session)
        assert running_experiment.state == "paused"

    def test_paused_to_running(self, app, running_experiment, db):
        transition(running_experiment, "paused", db.session)
        transition(running_experiment, "running", db.session)
        assert running_experiment.state == "running"

    def test_running_to_completed_with_results(self, app, experiment_with_result, db):
        transition(experiment_with_result, "completed", db.session)
        assert experiment_with_result.state == "completed"

    def test_paused_to_completed_with_results(self, app, experiment_with_result, db):
        transition(experiment_with_result, "paused", db.session)
        transition(experiment_with_result, "completed", db.session)
        assert experiment_with_result.state == "completed"


# ── Invalid Transitions ────────────────────────────────────────────────────────

class TestInvalidTransitions:

    def test_draft_to_completed_raises(self, app, draft_experiment, db):
        with pytest.raises(InvalidTransitionError):
            transition(draft_experiment, "completed", db.session)

    def test_draft_to_paused_raises(self, app, draft_experiment, db):
        with pytest.raises(InvalidTransitionError):
            transition(draft_experiment, "paused", db.session)

    def test_draft_to_draft_raises(self, app, draft_experiment, db):
        with pytest.raises(InvalidTransitionError):
            transition(draft_experiment, "draft", db.session)

    def test_completed_to_running_raises(self, app, completed_experiment, db):
        with pytest.raises(InvalidTransitionError):
            transition(completed_experiment, "running", db.session)

    def test_completed_to_draft_raises(self, app, completed_experiment, db):
        with pytest.raises(InvalidTransitionError):
            transition(completed_experiment, "draft", db.session)

    def test_completed_to_paused_raises(self, app, completed_experiment, db):
        with pytest.raises(InvalidTransitionError):
            transition(completed_experiment, "paused", db.session)

    def test_completed_is_terminal(self, app, completed_experiment, db):
        assert allowed_transitions("completed") == []

    def test_unknown_state_raises(self, app, draft_experiment, db):
        draft_experiment.state = "unknown_state"
        with pytest.raises(InvalidTransitionError):
            transition(draft_experiment, "running", db.session)


# ── Results Required ───────────────────────────────────────────────────────────

class TestResultsRequired:

    def test_running_to_completed_without_results_raises(self, app, running_experiment, db):
        with pytest.raises(ResultRequiredError):
            transition(running_experiment, "completed", db.session)

    def test_paused_to_completed_without_results_raises(self, app, running_experiment, db):
        transition(running_experiment, "paused", db.session)
        with pytest.raises(ResultRequiredError):
            transition(running_experiment, "completed", db.session)

    def test_running_to_completed_with_results_succeeds(self, app, experiment_with_result, db):
        transition(experiment_with_result, "completed", db.session)
        assert experiment_with_result.state == "completed"


# ── Timestamps ─────────────────────────────────────────────────────────────────

class TestTimestamps:

    def test_started_at_set_on_first_run(self, app, draft_experiment, db):
        assert draft_experiment.started_at is None
        transition(draft_experiment, "running", db.session)
        assert draft_experiment.started_at is not None

    def test_started_at_not_overwritten_on_resume(self, app, running_experiment, db):
        first_started = running_experiment.started_at
        transition(running_experiment, "paused", db.session)
        transition(running_experiment, "running", db.session)
        assert running_experiment.started_at == first_started

    def test_completed_at_set_on_completion(self, app, experiment_with_result, db):
        assert experiment_with_result.completed_at is None
        transition(experiment_with_result, "completed", db.session)
        assert experiment_with_result.completed_at is not None


# ── Allowed Transitions Helper ─────────────────────────────────────────────────

class TestAllowedTransitions:

    def test_draft_allowed(self):
        assert allowed_transitions("draft") == ["running"]

    def test_running_allowed(self):
        assert set(allowed_transitions("running")) == {"paused", "completed"}

    def test_paused_allowed(self):
        assert set(allowed_transitions("paused")) == {"running", "completed"}

    def test_completed_allowed(self):
        assert allowed_transitions("completed") == []

    def test_unknown_state_returns_empty(self):
        assert allowed_transitions("nonexistent") == []

    def test_all_states_covered_in_map(self):
        """Ensure VALID_TRANSITIONS covers all known states."""
        known_states = {"draft", "running", "paused", "completed"}
        assert set(VALID_TRANSITIONS.keys()) == known_states
