"""
State Machine — single source of truth for valid experiment transitions.

States:    draft → running → paused → completed
                         ↑________|

Rules:
  - completed is terminal (no exits)
  - completed requires at least one result logged
  - all transitions write an audit log entry
"""

from datetime import datetime, timezone
from ..errors import InvalidTransitionError, ResultRequiredError


# ── Transition Map ─────────────────────────────────────────────────────────────

VALID_TRANSITIONS: dict[str, list[str]] = {
    "draft":     ["running"],
    "running":   ["paused", "completed"],
    "paused":    ["running", "completed"],
    "completed": [],   # terminal — no exits
}

# States that require at least one result before entering
RESULTS_REQUIRED_FOR = {"completed"}


# ── Public API ─────────────────────────────────────────────────────────────────

def transition(experiment, to_state: str, db_session) -> None:
    """
    Attempt to move experiment to to_state.

    Raises:
        InvalidTransitionError  — if the transition is not allowed
        ResultRequiredError     — if results are required but missing
    """
    _assert_valid(experiment, to_state)
    _assert_results_if_required(experiment, to_state)

    old_state = experiment.state
    experiment.state = to_state
    _stamp_timestamps(experiment, to_state)
    _write_audit(experiment, old_state, to_state, db_session)


def allowed_transitions(current_state: str) -> list[str]:
    """Return list of states reachable from current_state."""
    return VALID_TRANSITIONS.get(current_state, [])


# ── Private Helpers ────────────────────────────────────────────────────────────

def _assert_valid(experiment, to_state: str) -> None:
    allowed = VALID_TRANSITIONS.get(experiment.state, [])
    if to_state not in allowed:
        raise InvalidTransitionError(
            f"Cannot transition from '{experiment.state}' to '{to_state}'. "
            f"Allowed transitions: {allowed or ['none (terminal state)']}"
        )


def _assert_results_if_required(experiment, to_state: str) -> None:
    if to_state in RESULTS_REQUIRED_FOR and not experiment.results:
        raise ResultRequiredError(
            f"Cannot move to '{to_state}' without logging at least one result first."
        )


def _stamp_timestamps(experiment, to_state: str) -> None:
    now = datetime.now(timezone.utc)
    if to_state == "running" and experiment.started_at is None:
        experiment.started_at = now
    if to_state == "completed":
        experiment.completed_at = now


def _write_audit(experiment, from_state: str, to_state: str, db_session) -> None:
    from ..models.audit_log import AuditLog

    log = AuditLog()
    log.experiment_id = experiment.id
    log.event_type = "state_change"
    log.from_state = from_state
    log.to_state = to_state
    log.metadata = {"triggered_by": "user"}

    db_session.add(log)
