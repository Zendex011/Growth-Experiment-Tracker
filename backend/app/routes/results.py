from flask import Blueprint, jsonify, request
from pydantic import ValidationError as PydanticValidationError

from ..schemas import CreateResultSchema
from ..services import experiment_service as svc
from ..errors import ValidationError

results_bp = Blueprint("results", __name__)


@results_bp.post("/<string:experiment_id>/results")
def add_result(experiment_id):
    try:
        data = CreateResultSchema.model_validate(request.get_json() or {})
    except PydanticValidationError as exc:
        raise ValidationError(str(exc))

    result = svc.add_result(
        experiment_id=experiment_id,
        control_value=data.control_value,
        variant_value=data.variant_value,
        sample_size_control=data.sample_size_control,
        sample_size_variant=data.sample_size_variant,
        duration_days=data.duration_days,
    )
    return jsonify(result.to_dict()), 201


@results_bp.get("/<string:experiment_id>/results")
def list_results(experiment_id):
    experiment = svc.get_by_id(experiment_id)
    return jsonify([r.to_dict() for r in experiment.results]), 200
