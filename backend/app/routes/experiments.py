from flask import Blueprint, jsonify, request
from pydantic import ValidationError as PydanticValidationError

from ..schemas import CreateExperimentSchema, UpdateVerdictSchema
from ..services import state_machine
from ..services import experiment_service as svc
from ..errors import ValidationError

experiments_bp = Blueprint("experiments", __name__)


@experiments_bp.get("/")
def list_experiments():
    state_filter = request.args.get("state")
    experiments = svc.get_all(state_filter=state_filter)
    return jsonify([e.to_dict() for e in experiments]), 200


@experiments_bp.post("/")
def create_experiment():
    try:
        data = CreateExperimentSchema.model_validate(request.get_json() or {})
    except PydanticValidationError as exc:
        raise ValidationError(str(exc))

    experiment = svc.create(
        title=data.title,
        hypothesis=data.hypothesis,
        metric_name=data.metric_name,
        metric_baseline=data.metric_baseline,
    )
    return jsonify(experiment.to_dict()), 201


@experiments_bp.get("/<string:experiment_id>")
def get_experiment(experiment_id):
    experiment = svc.get_by_id(experiment_id)
    return jsonify(
        experiment.to_dict(include_results=True, include_audit=True)
    ), 200


@experiments_bp.patch("/<string:experiment_id>/state")
def update_state(experiment_id):
    body = request.get_json() or {}
    to_state = body.get("state")

    if not to_state:
        raise ValidationError("Request body must include 'state'.")

    if to_state not in ("draft", "running", "paused", "completed"):
        raise ValidationError(
            f"'{to_state}' is not a valid state. "
            "Must be one of: draft, running, paused, completed."
        )

    experiment = svc.change_state(experiment_id, to_state)
    return jsonify({
        "id": experiment.id,
        "state": experiment.state,
        "allowed_next": state_machine.allowed_transitions(experiment.state),
    }), 200


@experiments_bp.post("/<string:experiment_id>/verdict")
def set_verdict(experiment_id):
    try:
        data = UpdateVerdictSchema.model_validate(request.get_json() or {})
    except PydanticValidationError as exc:
        raise ValidationError(str(exc))

    experiment = svc.set_verdict(
        experiment_id,
        verdict=data.verdict,
        verdict_reason=data.verdict_reason,
    )
    return jsonify(experiment.to_dict()), 200


@experiments_bp.delete("/<string:experiment_id>")
def delete_experiment(experiment_id):
    svc.delete(experiment_id)
    return jsonify({"deleted": experiment_id}), 200
