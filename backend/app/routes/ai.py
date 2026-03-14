from flask import Blueprint, jsonify, request
from pydantic import ValidationError as PydanticValidationError

from ..schemas.ai import HypothesisRequestSchema, VerdictRequestSchema
from ..services import ai_service
from ..services import experiment_service as svc
from ..errors import ValidationError, ConflictError

ai_bp = Blueprint("ai", __name__)


@ai_bp.post("/hypothesis")
def improve_hypothesis():
    """
    Takes a rough idea, returns an AI-structured hypothesis.
    AI output is NEVER saved here — frontend shows it, user accepts.
    """
    try:
        data = HypothesisRequestSchema.model_validate(request.get_json() or {})
    except PydanticValidationError as exc:
        raise ValidationError(str(exc))

    suggestion = ai_service.suggest_hypothesis(data.rough_idea)
    return jsonify(suggestion.model_dump()), 200


@ai_bp.post("/suggest-verdict")
def suggest_verdict():
    """
    Takes raw result numbers, returns an AI verdict suggestion.
    AI output is NEVER saved here — frontend shows it, user accepts.
    """
    try:
        data = VerdictRequestSchema.model_validate(request.get_json() or {})
    except PydanticValidationError as exc:
        raise ValidationError(str(exc))

    suggestion = ai_service.suggest_verdict(
        metric_name=data.metric_name,
        control_value=data.control_value,
        variant_value=data.variant_value,
        sample_size_control=data.sample_size_control,
        sample_size_variant=data.sample_size_variant,
        duration_days=data.duration_days,
    )
    return jsonify(suggestion.model_dump()), 200


@ai_bp.post("/summarize/<string:experiment_id>")
def summarize(experiment_id):
    """
    Generates a stakeholder summary for a completed experiment.
    Only works on completed experiments.
    AI output is NEVER saved here — frontend shows it, user copies.
    """
    experiment = svc.get_by_id(experiment_id)

    if experiment.state != "completed":
        raise ConflictError(
            f"Summaries can only be generated for completed experiments. "
            f"Current state: '{experiment.state}'."
        )

    experiment_dict = experiment.to_dict(include_results=True)
    suggestion = ai_service.summarize_experiment(experiment_dict)
    return jsonify(suggestion.model_dump()), 200
