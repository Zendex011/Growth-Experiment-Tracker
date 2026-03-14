"""
Experiment Service — all business logic for experiments.

Routes call this service. This service calls the state machine.
No route ever touches the DB directly.
"""

from datetime import datetime, timezone
from ..extensions import db
from ..models.experiment import Experiment
from ..models.result import ExperimentResult
from ..models.audit_log import AuditLog
from ..errors import NotFoundError, ConflictError, VerdictAlreadySetError
from ..services.state_machine import transition, allowed_transitions


# ── Queries ────────────────────────────────────────────────────────────────────

def get_all(state_filter: str = None) -> list[Experiment]:
    query = Experiment.query.order_by(Experiment.created_at.desc())
    if state_filter:
        query = query.filter(Experiment.state == state_filter)
    return query.all()


def get_by_id(experiment_id: str) -> Experiment:
    experiment = Experiment.query.get(experiment_id)
    if not experiment:
        raise NotFoundError(f"Experiment '{experiment_id}' not found.")
    return experiment


# ── Mutations ──────────────────────────────────────────────────────────────────

def create(title: str, hypothesis: str, metric_name: str, metric_baseline: float) -> Experiment:
    experiment = Experiment(
        title=title,
        hypothesis=hypothesis,
        metric_name=metric_name,
        metric_baseline=metric_baseline,
        state="draft",
    )
    db.session.add(experiment)
    db.session.flush()

    # Audit creation
    log = AuditLog()
    log.experiment_id = experiment.id
    log.event_type = "created"
    log.data = {"title": title}
    db.session.add(log)

    db.session.commit()
    return experiment


def change_state(experiment_id: str, to_state: str) -> Experiment:
    experiment = get_by_id(experiment_id)
    transition(experiment, to_state, db.session)
    db.session.commit()
    return experiment


def set_verdict(experiment_id: str, verdict: str, verdict_reason: str = None) -> Experiment:
    experiment = get_by_id(experiment_id)

    if experiment.state != "completed":
        raise ConflictError(
            f"Verdict can only be set on completed experiments. "
            f"Current state: '{experiment.state}'."
        )

    if experiment.verdict is not None:
        raise VerdictAlreadySetError(
            f"Verdict is already set to '{experiment.verdict}' and cannot be changed."
        )

    experiment.verdict = verdict
    experiment.verdict_reason = verdict_reason

    log = AuditLog()
    log.experiment_id = experiment.id
    log.event_type = "verdict_set"
    log.data = {"verdict": verdict, "reason": verdict_reason}
    db.session.add(log)

    db.session.commit()
    return experiment


def delete(experiment_id: str) -> None:
    experiment = get_by_id(experiment_id)

    if experiment.state != "draft":
        raise ConflictError(
            f"Only draft experiments can be deleted. "
            f"Current state: '{experiment.state}'."
        )

    db.session.delete(experiment)
    db.session.commit()


# ── Results ────────────────────────────────────────────────────────────────────

def add_result(
    experiment_id: str,
    control_value: float,
    variant_value: float,
    sample_size_control: int,
    sample_size_variant: int,
    duration_days: int,
) -> ExperimentResult:
    experiment = get_by_id(experiment_id)

    if experiment.state != "running":
        raise ConflictError(
            f"Results can only be added to running experiments. "
            f"Current state: '{experiment.state}'."
        )

    result = ExperimentResult(
        experiment_id=experiment_id,
        control_value=control_value,
        variant_value=variant_value,
        sample_size_control=sample_size_control,
        sample_size_variant=sample_size_variant,
        duration_days=duration_days,
    )
    db.session.add(result)

    log = AuditLog()
    log.experiment_id = experiment_id
    log.event_type = "result_added"
    log.data = {
        "control_value": control_value,
        "variant_value": variant_value,
    }
    db.session.add(log)

    db.session.commit()
    return result
